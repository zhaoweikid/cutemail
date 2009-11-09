#!/usr/bin/python
# coding: utf-8
import os, sys, cStringIO, string, time
import simplejson
import wx
import wx.aui
import wx.wizard as wiz
import wx.lib.sized_controls as sc
from wx.lib.wordwrap import wordwrap
from   picmenu import PicMenu
from   listindex import *
import treelist, viewhtml, contact
import config, common, dbope, useradd, logfile
import writer, userbox, search
import cPickle as pickle
import pop3, mailparse, utils
from logfile import loginfo, logerr, logwarn

class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(1000, 618), 
                            name="CuteMail", style=wx.DEFAULT_FRAME_STYLE )
        
        self.mgr = wx.aui.AuiManager()
        self.mgr.SetManagedWindow(self)
        
        self.rundir = os.path.dirname(os.path.abspath(sys.argv[0])).replace("\\", "/")
        self.bmpdir = os.path.join(self.rundir, "bitmaps")
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.BitmapFromImage(wx.Image((self.bmpdir + "/cutemail.png"), wx.BITMAP_TYPE_PNG)))
        self.SetIcon(icon)
        
        # 当前mailbox
        self.last_mailbox = ''
        # 以邮箱路径为索引存储MailListPane
        self.mailboxs = {}

        # 初始化常量
        self.init_const()
        # 创建菜单        
        self.make_menu()
        # 创建工具栏
        self.make_toolbar()
        # 创建状态栏
        self.make_statusbar()
        
        # 创建用户信箱树形结构
        self.tree = treelist.MailboxTree(self)
        
        # 创建显示邮件控件, 为每个用户的每个邮箱路径都创建一个
        self.init_data()
        # 把邮件信息加载进来        
        self.load_db_data()
        
        # 获取所有用户名
        ks = config.cf.users.keys()
        # 第一个用户名
        # 当前选择的mailbox
        
        if ks:
            self.last_mailbox = '/'+ks[0]
        else:
            self.last_mailbox = '/'
        
        # 内容显示控件
        self.listcnt = viewhtml.ViewHtml(self)
        self.listcnt.Hide()
        
        # 附件显示控件
        self.attachctl = viewhtml.AttachListCtrl(self, self.rundir)
        self.attachctl.Hide()
        # 联系人 
        self.contact = contact.ContactTree(self, self.rundir)
        self.contact.Hide()
        
        self.mgr.AddPane(self.contact, wx.aui.AuiPaneInfo().Name("contact").Caption(u"联系人").
                    Right().Layer(0).Position(2).CloseButton(True).MaximizeButton(False))
        self.mgr.GetPane('contact').Hide()

        # 为面板管理器增加用户邮箱树形结构
        self.mgr.AddPane(self.tree, wx.aui.AuiPaneInfo().Name("tree").Caption(u"用户").
                          Left().Layer(1).Position(1).CloseButton(False).MaximizeButton(False))
            
        # 把邮件内容面板添加到面板管理器
        self.mgr.AddPane(self.listcnt, wx.aui.AuiPaneInfo().Name("listcnt").Caption(u"邮件内容").
                          MinSize(wx.Size(-1, 200)).
                          Bottom().Layer(0).Position(1).CloseButton(True).MaximizeButton(True))
        
        self.mgr.AddPane(self.attachctl, wx.aui.AuiPaneInfo().Name("attachctl").Caption(u"附件内容").
                          MinSize(wx.Size(48,-1)).Bottom().
                          Layer(0).Position(4).CloseButton(True).MaximizeButton(True))
        # 显示当前选择的邮件列表面板
        loginfo('show:', self.last_mailbox)
        self.mgr.GetPane(self.last_mailbox).Show()
        self.mgr.GetPane('attachctl').Hide()
        self.mgr.Update()
        
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer = wx.Timer(self)
        self.timer.Start(1000)
        
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_SIZE, self.OnSize)


        self.mail_writer_item = ['subject', 'from', 'to', 'text', 'user', 'attach']

        
    def add_mailbox_panel(self, k, obj=None):
        loginfo('add panel:', k)
        if not obj:
            if k.count('/') == 1:
                obj = userbox.UserBoxInfo(self, k)
            else:
                obj = treelist.MailListPanel(self, k)
        obj.Hide()
        self.mailboxs[k] = obj
        self.mgr.AddPane(obj, wx.aui.AuiPaneInfo().Name(k).CenterPane().Hide())
        return obj
        
        
    def init_data(self):
        mailboxkeys = self.mailboxs.keys()
        loginfo('mailboxkeys:', mailboxkeys)
        for k in mailboxkeys:
            loginfo('init data:', k)
            if not self.mailboxs[k]:
                self.add_mailbox_panel(k)
        k = u'/'
        obj = viewhtml.ViewHtml(self)
        obj.set_url('http://code.google.com/p/cutemail')
        self.add_mailbox_panel(k, obj)
 
    def load_db_info(self, user, row):
        row['attach'] = simplejson.loads(row['attach'])
        att = 0
        #loginfo('load_db_info:', row['attach'])
        if len(row['attach']) > 0:
            att = 1
                
        boxname = '/%s/' % (user) + config.cf.mailbox_map_en2cn[row['mailbox']]
        row['user'] = user
        row['box'] = boxname
        row['filepath'] = os.path.join(config.cf.datadir, user, row['mailbox'], row['filename'].lstrip(os.sep))

        mailaddr = row['mailfrom']
        if row['mailbox'] in ['send','draft','sendover']:
            mailaddr = row['mailto']
        else:
            if row['fromuser']:
                mailaddr = row['fromuser']
        item = [mailaddr, att, row['subject'], 1, row['date'],wx.TreeItemData(row)]
            #print item
        panel = self.mailboxs[boxname]
        return panel.add_mail(item)
        
    def load_db_one(self, user, mid):
        dbpath = os.path.join(config.cf.datadir, user, 'mailinfo.db')
        loginfo('load db from path:', dbpath)
        conn = dbope.DBOpe(dbpath)
        try:
            ret = conn.query("select id,filename,subject,fromuser,mailfrom,mailto,size,ctime,datetime(date,'unixepoch') as date,attach,mailbox,status from mailinfo where id=" + str(mid))
        finally:
            conn.close()
        if not ret:
            return None
        #for row in ret:
        row = ret[0]
        return self.load_db_info(user, row)
        
    def load_db_data(self):
        users = config.cf.users
        for u in users:
            #mlist = self.mailboxs['/%s/' % (u) + u'收件箱']
            dbpath = os.path.join(config.cf.datadir, u, 'mailinfo.db')
            loginfo('load db from path:', dbpath)
            conn = dbope.DBOpe(dbpath)
            try:
                ret = conn.query("select id,filename,subject,fromuser,mailfrom,mailto,size,ctime,datetime(date,'unixepoch') as date,attach,mailbox,status from mailinfo order by date")
            finally:
                conn.close()
            for row in ret:
                self.load_db_info(u, row) 


    def init_const(self):
        self.ID_FILE_OPEN          = wx.NewId()
        self.ID_FILE_SAVE_AS       = wx.NewId()
        self.ID_FILE_GET_MAIL      = wx.NewId()
        self.ID_FILE_SEND_MAIL     = wx.NewId()
        self.ID_FILE_GET_ALL_MAIL  = wx.NewId()
        self.ID_FILE_SEND_ALL_MAIL = wx.NewId()
        self.ID_FILE_IMPORT        = wx.NewId()
        self.ID_FILE_EXPORT        = wx.NewId()
        self.ID_FILE_EXIT          = wx.NewId()

        self.ID_VIEW_MAIL    = wx.NewId()
        self.ID_VIEW_ATTACH  = wx.NewId()
        self.ID_VIEW_CONTACT = wx.NewId()
        #self.ID_VIEW_SEARCH  = wx.NewId()
        self.ID_VIEW_ENCODE  = wx.NewId()
        self.ID_VIEW_SOURCE  = wx.NewId()
        
        self.ID_VIEW_TEMPLATE   = wx.NewId()
        
        self.ID_MAIL_WRITE     = wx.NewId()
        self.ID_MAIL_REPLY     = wx.NewId()
        self.ID_MAIL_REPLY_ALL = wx.NewId()
        self.ID_MAIL_FORWARD   = wx.NewId()
        self.ID_MAIL_SEND_SEC  = wx.NewId()
        self.ID_MAIL_ATTACH    = wx.NewId()
       
        self.ID_MAIL_SELECTALL = wx.NewId()
        self.ID_MAIL_COPYTO    = wx.NewId()
        self.ID_MAIL_MOVETO    = wx.NewId()
        self.ID_MAIL_DEL       = wx.NewId()
        self.ID_MAIL_FLAG      = wx.NewId()
        self.ID_MAIL_SEARCH    = wx.NewId()
 
        self.ID_MAILBOX_USER_NEW            = wx.NewId()
        self.ID_MAILBOX_USER_RENAME         = wx.NewId()
        self.ID_MAILBOX_USER_DEL            = wx.NewId()
        self.ID_MAILBOX_USER_OPTIONS        = wx.NewId()
       
        self.ID_MAILBOX_NEW         = wx.NewId()
        self.ID_MAILBOX_RENAME      = wx.NewId()
        self.ID_MAILBOX_DEL         = wx.NewId()
        self.ID_MAILBOX_CLEAR_TRASH = wx.NewId()
        self.ID_MAILBOX_CLEAR_SPAM  = wx.NewId()
 
        self.ID_MAILBOX_IMPORT     = wx.NewId()
        self.ID_MAILBOX_EXPORT     = wx.NewId()
       
        self.ID_HELP          = wx.NewId()
        self.ID_HELP_UPDATE   = wx.NewId()
        self.ID_HELP_ABOUT    = wx.NewId()
        
        self.ID_IMPORT_MAB_USER       = wx.NewId()
        self.ID_IMPORT_MAB_MAILBOX    = wx.NewId()
        self.ID_IMPORT_MAB_LINKMAN    = wx.NewId()
        self.ID_IMPORT_OUTLOOK_USER    = wx.NewId()
        self.ID_IMPORT_OUTLOOK_MAILBOX = wx.NewId()
        self.ID_IMPORT_OUTLOOK_LINKMAN = wx.NewId()
        self.ID_IMPORT_FOXMAIL_USER    = wx.NewId()
        self.ID_IMPORT_FOXMAIL_MAILBOX = wx.NewId()
        self.ID_IMPORT_FOXMAIL_LINKMAN = wx.NewId()
        
        self.ID_EXPORT_MAB_USER       = wx.NewId()
        self.ID_EXPORT_MAB_MAILBOX    = wx.NewId()
        self.ID_EXPORT_MAB_LINKMAN    = wx.NewId()
        
        self.ID_ENCODING_AUTO     = wx.NewId()
        self.ID_ENCODING_GB2312   = wx.NewId()
        self.ID_ENCODING_GBK      = wx.NewId()
        self.ID_ENCODING_GB18030  = wx.NewId()
        self.ID_ENCODING_BIG5     = wx.NewId()
        self.ID_ENCODING_UTF8     = wx.NewId()
        self.ID_ENCODING_EUC      = wx.NewId()
        self.ID_ENCODING_SHIFTJIS = wx.NewId()
        self.ID_ENCODING_KOREA    = wx.NewId()
        
    def make_toolbar(self):
        self.ID_TOOLBAR_MAIL_GET = wx.NewId()
        self.ID_TOOLBAR_MAIL_SEND = wx.NewId()
        self.ID_TOOLBAR_MAIL_NEW = wx.NewId()
        self.ID_TOOLBAR_MAIL_REPLY = wx.NewId()
        self.ID_TOOLBAR_MAIL_FORWARD = wx.NewId()
        self.ID_TOOLBAR_MAIL_DELETE = wx.NewId()
        self.ID_TOOLBAR_ADDR = wx.NewId()
        #self.ID_TOOLBAR_FIND = wx.NewId()
        self.ID_TOOLBAR_WWW = wx.NewId()
        
        self.toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.Size(48, 48), wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_TEXT)
        self.toolbar.SetToolBitmapSize(wx.Size (48, 48))
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_MAIL_GET, u"收邮件", common.load_bitmap('bitmaps/32/mail_get.png'), shortHelp=u"收取邮件", longHelp=u"收取邮件")
        #self.toolbar.AddLabelTool(3401, 'aaaa', common.load_bitmap('bitmaps/32/mail_get.png'),shortHelp="收取邮件", longHelp="收取邮件")
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_MAIL_SEND, u'发送', common.load_bitmap('bitmaps/32/mail_send.png'),  shortHelp=u"发送候发邮件", longHelp=u"发送候发邮件")
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_MAIL_NEW, u'新邮件', common.load_bitmap('bitmaps/32/mail_new.png'),  shortHelp=u"写新邮件", longHelp=u"写新邮件")
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_MAIL_REPLY, u'回复', common.load_bitmap('bitmaps/32/mail_reply.png'), shortHelp=u"回复", longHelp=u"回复")
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_MAIL_FORWARD, u'转发', common.load_bitmap('bitmaps/32/mail_forward.png'), shortHelp=u"转发", longHelp=u"转发")
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_MAIL_DELETE, u'删除', common.load_bitmap('bitmaps/32/mail_delete.png'), shortHelp=u"删除", longHelp=u"删除")
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_ADDR, u'联系人', common.load_bitmap('bitmaps/32/toggle_log.png'), shortHelp=u"地址薄", longHelp=u"地址薄")
        #self.toolbar.AddLabelTool(self.ID_TOOLBAR_FIND, u'查找', common.load_bitmap('bitmaps/32/filefind.png'), shortHelp=u"查找", longHelp=u"查找")
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_WWW, u'主页', common.load_bitmap('bitmaps/32/home.png'), shortHelp=u"主页", longHelp=u"主页")
        self.toolbar.AddSeparator()

        searchctl = search.MailSearchCtrl(self.toolbar, size=(150,-1), doSearch=self.DoSearch)
        self.toolbar.AddControl(searchctl)

        self.toolbar.Realize ()
        self.SetToolBar(self.toolbar)
        
        self.Bind(wx.EVT_TOOL, self.OnFileGetMail, id=self.ID_TOOLBAR_MAIL_GET)
        self.Bind(wx.EVT_TOOL, self.OnFileSendMail, id=self.ID_TOOLBAR_MAIL_SEND)
        self.Bind(wx.EVT_TOOL, self.OnMailWrite, id=self.ID_TOOLBAR_MAIL_NEW)
        self.Bind(wx.EVT_TOOL, self.OnMailReply, id=self.ID_TOOLBAR_MAIL_REPLY)
        self.Bind(wx.EVT_TOOL, self.OnMailForward, id=self.ID_TOOLBAR_MAIL_FORWARD)
        self.Bind(wx.EVT_TOOL, self.OnMailDel, id=self.ID_TOOLBAR_MAIL_DELETE)
        self.Bind(wx.EVT_TOOL, self.OnViewContact, id=self.ID_TOOLBAR_ADDR)
        #self.Bind(wx.EVT_TOOL, self.OnMailSearch, id=self.ID_TOOLBAR_FIND)
        self.Bind(wx.EVT_TOOL, self.OnWebsite, id=self.ID_TOOLBAR_WWW)
        
    def make_menu(self):        
        self.filemenu = PicMenu(self)        
        self.filemenu.Append(self.ID_FILE_OPEN, u"打开", "open.png")        
        self.filemenu.Append(self.ID_FILE_SAVE_AS, u"另存为", "saveas.png")    
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_FILE_GET_MAIL, u'收取邮件', "mail_get.png")
        self.filemenu.Append(self.ID_FILE_SEND_MAIL, u'发送邮件', "mail_send.png")
        self.filemenu.Append(self.ID_FILE_GET_ALL_MAIL, u'收取所有帐户邮件', "mail_get.png")
        self.filemenu.Append(self.ID_FILE_SEND_ALL_MAIL, u'发送所有帐户邮件', "mail_send.png")      
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_FILE_IMPORT, u'导入邮件', "down.png")
        self.filemenu.Append(self.ID_FILE_EXPORT, u'导出邮件', "up.png")
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_FILE_EXIT, u'退出', "exit.png")      

        encodingmenu = wx.Menu()
        encodingmenu.Append(self.ID_ENCODING_AUTO, u"自动选择")
        encodingmenu.Append(self.ID_ENCODING_GB2312, u"简体中文(gb2312)")
        encodingmenu.Append(self.ID_ENCODING_GBK, u"简体中文(gbk)")
        encodingmenu.Append(self.ID_ENCODING_GB18030, u"简体中文(gb18030)")
        encodingmenu.Append(self.ID_ENCODING_BIG5, u"繁体中文(big5)")
        encodingmenu.Append(self.ID_ENCODING_UTF8, u"UTF-8")
        encodingmenu.AppendSeparator()
        encodingmenu.Append(self.ID_ENCODING_EUC, u"日文(EUC)")
        encodingmenu.Append(self.ID_ENCODING_SHIFTJIS, u"日文(Shift-JIS)")
        encodingmenu.AppendSeparator()
        encodingmenu.Append(self.ID_ENCODING_KOREA, u"韩文")
        
        self.viewmenu = PicMenu(self)
        self.viewmenu.Append(self.ID_VIEW_MAIL, u"邮件内容窗口", 'contents.png')        
        self.viewmenu.Append(self.ID_VIEW_ATTACH, u"附件内容窗口", 'attach.png')        
        self.viewmenu.Append(self.ID_VIEW_CONTACT, u"联系人窗口", 'contact.png')        
        self.viewmenu.Append(self.ID_VIEW_SOURCE, u"信件原文", 'note.png')
        #self.viewmenu.Append(self.ID_VIEW_SEARCH, u"查找邮件", 'mail_find.png')
        self.viewmenu.AppendSeparator()
        self.viewmenu.Append(self.ID_VIEW_TEMPLATE, u"模板管理", "template.png")

        self.viewmenu.AppendSeparator()
        self.viewmenu.AppendMenu(self.ID_VIEW_ENCODE, u"编码", encodingmenu)

        self.mailmenu = PicMenu(self)
        self.mailmenu.Append(self.ID_MAIL_WRITE, u"写新邮件", 'mail_new.png')
        self.mailmenu.Append(self.ID_MAIL_REPLY, u"回复邮件", 'mail_reply.png')
        self.mailmenu.Append(self.ID_MAIL_REPLY_ALL, u"回复全部", 'mail_replyall.png')
        self.mailmenu.Append(self.ID_MAIL_FORWARD, u"转发邮件", 'mail_send.png')            
        self.mailmenu.Append(self.ID_MAIL_SEND_SEC, u"再次发送", 'mail_send.png')
        self.mailmenu.Append(self.ID_MAIL_ATTACH, u"作为附件发送", 'mail_send.png')
        self.mailmenu.AppendSeparator()
        
        self.mailmenu.Append(self.ID_MAIL_SELECTALL, u"选择所有", 'check.png')
        self.mailmenu.Append(self.ID_MAIL_COPYTO, u"复制到", 'editcopy.png')
        self.mailmenu.Append(self.ID_MAIL_MOVETO, u"移动到", 'editcut.png')
        self.mailmenu.Append(self.ID_MAIL_DEL, u"删除", 'editdelete.png')
        self.mailmenu.AppendSeparator()
        self.mailmenu.Append(self.ID_MAIL_FLAG, u"标记为", 'flag.png')
        self.mailmenu.Append(self.ID_MAIL_SEARCH, u"查找", 'mail_find.png') 
        
        self.mailboxmenu = PicMenu(self)
        self.mailboxmenu.Append(self.ID_MAILBOX_USER_NEW, u"新建邮箱帐户", 'user.png')        
        self.mailboxmenu.Append(self.ID_MAILBOX_USER_RENAME, u"更名邮箱帐户", 'user.png')
        self.mailboxmenu.Append(self.ID_MAILBOX_USER_DEL, u"删除邮箱帐户", "user.png")
        self.mailboxmenu.AppendSeparator()

        self.mailboxmenu.Append(self.ID_MAILBOX_NEW, u"新建邮件夹", 'folder_open.png')
        self.mailboxmenu.Append(self.ID_MAILBOX_RENAME, u"邮件夹改名", 'folder_red.png')
        self.mailboxmenu.Append(self.ID_MAILBOX_DEL, u"删除邮件夹", 'folder_grey.png')
        self.mailboxmenu.AppendSeparator()
        self.mailboxmenu.Append(self.ID_MAILBOX_CLEAR_TRASH, u"清空删除邮件")
        self.mailboxmenu.Append(self.ID_MAILBOX_CLEAR_SPAM, u"清空垃圾邮件")   
        
        importmenu = wx.Menu()
        importmenu.Append(self.ID_IMPORT_MAB_USER, u"导入cutemail帐户")
        importmenu.Append(self.ID_IMPORT_MAB_MAILBOX, u"导入cutemail邮件")
        importmenu.Append(self.ID_IMPORT_MAB_LINKMAN, u"导入cutemail联系人")
        importmenu.AppendSeparator()
        importmenu.Append(self.ID_IMPORT_OUTLOOK_USER, u"导入outlook帐户")
        importmenu.Append(self.ID_IMPORT_OUTLOOK_MAILBOX, u"导入outlook邮件")
        importmenu.Append(self.ID_IMPORT_OUTLOOK_LINKMAN, u"导入outlook联系人")
        importmenu.AppendSeparator()
        importmenu.Append(self.ID_IMPORT_FOXMAIL_USER, u"导入foxmail帐户")
        importmenu.Append(self.ID_IMPORT_FOXMAIL_MAILBOX, u"导入foxmail邮件")
        importmenu.Append(self.ID_IMPORT_FOXMAIL_LINKMAN, u"导入foxmail联系人")
        
        exportmenu = wx.Menu()        
        exportmenu.Append(self.ID_EXPORT_MAB_USER, u"导出cutemail帐户")
        exportmenu.Append(self.ID_EXPORT_MAB_MAILBOX, u"导出cutemail邮件")
        exportmenu.Append(self.ID_EXPORT_MAB_LINKMAN, u"导出cutemail联系人")
       
        self.mailboxmenu.AppendSeparator()
        self.mailboxmenu.AppendMenu(self.ID_MAILBOX_IMPORT, u"导入账户/邮件/联系人", importmenu)
        self.mailboxmenu.AppendMenu(self.ID_MAILBOX_EXPORT, u"导出账户/邮件/联系人", exportmenu)
        
        self.mailboxmenu.AppendSeparator()
        self.mailboxmenu.Append(self.ID_MAILBOX_USER_OPTIONS, u"属性", 'preferences.png')       
        
        self.helpmenu = PicMenu(self)
        self.helpmenu.Append(self.ID_HELP, u"帮助主题", 'help.png')      
        self.helpmenu.AppendSeparator()
        self.helpmenu.Append(self.ID_HELP_UPDATE, u"检查更新", 'help.png') 
        self.helpmenu.Append(self.ID_HELP_ABOUT, u"关于", 'info.png')
        
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.filemenu,u"文件")        
        self.menuBar.Append(self.viewmenu,u"查看")
        self.menuBar.Append(self.mailmenu,u"邮件")
        self.menuBar.Append(self.mailboxmenu,u"邮箱")
        self.menuBar.Append(self.helpmenu,u"帮助")
        self.SetMenuBar(self.menuBar)

        self.Bind(wx.EVT_MENU, self.OnFileOpen, id=self.ID_FILE_OPEN)
        self.Bind(wx.EVT_MENU, self.OnFileSaveAs, id=self.ID_FILE_SAVE_AS)
        self.Bind(wx.EVT_MENU, self.OnFileGetMail, id=self.ID_FILE_GET_MAIL)
        self.Bind(wx.EVT_MENU, self.OnFileSendMail, id=self.ID_FILE_SEND_MAIL)
        self.Bind(wx.EVT_MENU, self.OnFileGetAllMail, id=self.ID_FILE_GET_ALL_MAIL)
        self.Bind(wx.EVT_MENU, self.OnFileSendAllMail, id=self.ID_FILE_SEND_ALL_MAIL)
        self.Bind(wx.EVT_MENU, self.OnFileImport, id=self.ID_FILE_IMPORT)
        self.Bind(wx.EVT_MENU, self.OnFileExport, id=self.ID_FILE_EXPORT)
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=self.ID_FILE_EXIT)
        
        self.Bind(wx.EVT_MENU, self.OnViewMail, id=self.ID_VIEW_MAIL)
        self.Bind(wx.EVT_MENU, self.OnViewAttach, id=self.ID_VIEW_ATTACH)
        self.Bind(wx.EVT_MENU, self.OnViewContact, id=self.ID_VIEW_CONTACT)
        self.Bind(wx.EVT_MENU, self.OnViewSource, id=self.ID_VIEW_SOURCE)
        #self.Bind(wx.EVT_MENU, self.OnMailSearch, id=self.ID_VIEW_SEARCH)
        self.Bind(wx.EVT_MENU, self.OnViewEncode, id=self.ID_VIEW_ENCODE)
        
        self.Bind(wx.EVT_MENU, self.OnImportOutlookUser, id=self.ID_IMPORT_OUTLOOK_USER)
        self.Bind(wx.EVT_MENU, self.OnImportOutlookMailbox, id=self.ID_IMPORT_OUTLOOK_MAILBOX)
        self.Bind(wx.EVT_MENU, self.OnImportOutlookLinkman, id=self.ID_IMPORT_OUTLOOK_LINKMAN)
        self.Bind(wx.EVT_MENU, self.OnImportFoxmailUser, id=self.ID_IMPORT_FOXMAIL_USER)
        self.Bind(wx.EVT_MENU, self.OnImportFoxmailMailbox, id=self.ID_IMPORT_FOXMAIL_MAILBOX)
        self.Bind(wx.EVT_MENU, self.OnImportFoxmailLinkman, id=self.ID_IMPORT_FOXMAIL_LINKMAN)
        self.Bind(wx.EVT_MENU, self.OnImportCuteUser, id=self.ID_IMPORT_MAB_USER)
        self.Bind(wx.EVT_MENU, self.OnImportCuteMailbox, id=self.ID_IMPORT_MAB_MAILBOX)
        self.Bind(wx.EVT_MENU, self.OnImportCuteLinkman, id=self.ID_IMPORT_MAB_LINKMAN)
        
        self.Bind(wx.EVT_MENU, self.OnExportCuteUser, id=self.ID_EXPORT_MAB_USER)
        self.Bind(wx.EVT_MENU, self.OnExportCuteMailbox, id=self.ID_EXPORT_MAB_MAILBOX)
        self.Bind(wx.EVT_MENU, self.OnExportCuteLinkman, id=self.ID_EXPORT_MAB_LINKMAN)
        
        self.Bind(wx.EVT_MENU, self.OnViewTemplate, id=self.ID_VIEW_TEMPLATE)

        self.Bind(wx.EVT_MENU, self.OnMailboxUserNew, id=self.ID_MAILBOX_USER_NEW)
        self.Bind(wx.EVT_MENU, self.OnMailboxUserRename, id=self.ID_MAILBOX_USER_RENAME)
        self.Bind(wx.EVT_MENU, self.OnMailboxUserDel, id=self.ID_MAILBOX_USER_DEL)
        self.Bind(wx.EVT_MENU, self.OnMailboxUserOptions, id=self.ID_MAILBOX_USER_OPTIONS)
        
        self.Bind(wx.EVT_MENU, self.OnMailWrite, id=self.ID_MAIL_WRITE)
        self.Bind(wx.EVT_MENU, self.OnMailReply, id=self.ID_MAIL_REPLY)
        self.Bind(wx.EVT_MENU, self.OnMailReplyAll, id=self.ID_MAIL_REPLY_ALL)
        self.Bind(wx.EVT_MENU, self.OnMailForward, id=self.ID_MAIL_FORWARD)
        self.Bind(wx.EVT_MENU, self.OnMailSendSec, id=self.ID_MAIL_SEND_SEC)
        self.Bind(wx.EVT_MENU, self.OnMailAttach, id=self.ID_MAIL_ATTACH)
        self.Bind(wx.EVT_MENU, self.OnMailSelectAll, id=self.ID_MAIL_SELECTALL)
        self.Bind(wx.EVT_MENU, self.OnMailCopyTo, id=self.ID_MAIL_COPYTO)
        self.Bind(wx.EVT_MENU, self.OnMailMoveTo, id=self.ID_MAIL_MOVETO)
        self.Bind(wx.EVT_MENU, self.OnMailDel, id=self.ID_MAIL_DEL)
        self.Bind(wx.EVT_MENU, self.OnMailFlag, id=self.ID_MAIL_FLAG)
        #self.Bind(wx.EVT_MENU, self.OnMailSearch, id=self.ID_MAIL_SEARCH)
        
        self.Bind(wx.EVT_MENU, self.OnMailboxNew, id=self.ID_MAILBOX_NEW)
        self.Bind(wx.EVT_MENU, self.OnMailboxRename, id=self.ID_MAILBOX_RENAME)
        self.Bind(wx.EVT_MENU, self.OnMailboxDel, id=self.ID_MAILBOX_DEL)
        self.Bind(wx.EVT_MENU, self.OnMailboxClearTrash, id=self.ID_MAILBOX_CLEAR_TRASH)
        self.Bind(wx.EVT_MENU, self.OnMailboxClearSpam, id=self.ID_MAILBOX_CLEAR_SPAM)


        self.Bind(wx.EVT_MENU, self.OnHelp, id=self.ID_HELP)
        self.Bind(wx.EVT_MENU, self.OnHelpUpdate, id=self.ID_HELP_UPDATE)
        self.Bind(wx.EVT_MENU, self.OnHelpAbout, id=self.ID_HELP_ABOUT)
        
    def make_statusbar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.SetStatusWidths([-1, -2, -1])
        
    def display_mailbox(self, name):
        loginfo('display name:', name)
        try:
            newobj = self.mailboxs[name]
        except Exception, e:
            logerr('mailbox error:', e)
            return False
        
        loginfo('display:', self.last_mailbox, name)
        
        try:
            if self.last_mailbox:
                self.mgr.GetPane(self.last_mailbox).Hide()
            self.mgr.GetPane(name).Show()
            self.mgr.Update()
            self.last_mailbox = name       
        except Exception, e:
            logerr('display_mailbox:', e)
        return True
        
    def DoSearch(self, text):
        loginfo('search:', text)
        return True

    def OnCloseWindow(self, event):
        self.Hide()
        self.mgr.UnInit()
        del self.mgr
        self.Destroy()
        sys.exit()

    def OnSize(self, event):
        self.Refresh()
            
    def OnTimer(self, event):
        '''
        定时任务
        '''
        #print 'time now', time.ctime()
        for i in range(0,5):
            try:
                item = config.uiq.get(0)
            except:
                break
            else:
                loginfo('timer get uiq: ', item)
                name = item['name']
                task = item['task']
                boxpanel = self.mailboxs['/%s/' % (name) + u'收件箱']
                if task == 'updatebox':
                    usercf = config.cf.users[name]
                    dbpath = os.path.join(config.cf.datadir, name, 'mailinfo.db')
                    conn = dbope.DBOpe(dbpath, 'w')
                    try:
                        count = conn.query('select count(*) as count from mailinfo')[0]['count']
                        ret = conn.query("select id,filename,subject,fromuser,mailfrom,mailto,size,ctime,datetime(date,'unixepoch') as date,attach,mailbox,status from mailinfo where status='new' and mailbox='recv'")
                        if ret:
                            for info in ret:
                                loginfo('get mail:', info['filename'])
                                info['status'] = 'noread'
                                self.load_db_info(name, info)
                                conn.execute("update mailinfo set status='noread' where id=" + str(info['id']))
                    finally:
                        conn.close()

                    self.statusbar.SetStatusText(u'最后收信时间: %d-%02d-%02d %02d:%02d:%02d' % time.localtime()[:6], 1)
                elif task == 'newmail':
                    filename = item['filename']
                    usercf = config.cf.users[name]
                    dbpath = os.path.join(config.cf.datadir, name, 'mailinfo.db')
                    conn = dbope.DBOpe(dbpath, 'w')
                    try:
                        ret = conn.query("select id,filename,subject,fromuser,mailfrom,mailto,size,ctime,datetime(date,'unixepoch') as date,attach,mailbox,status from mailinfo where filename='%s'" % (filename))
                        if ret:
                            for info in ret:
                                loginfo('get mail:', info['filename'])
                                info['status'] = 'noread'
                                self.load_db_info(name, info)
                                conn.execute("update mailinfo set status='noread' where id=" + str(info['id']))
                    finally:
                        conn.close()

                    self.statusbar.SetStatusText(u'最后收信时间: %d-%02d-%02d %02d:%02d:%02d' % time.localtime()[:6], 1)
                    s = u'%s 收信 %d/%d' % (name, item['count'], item['allcount'])
                    self.statusbar.SetStatusText(s, 0)

                elif task == 'alert':
                    wx.MessageBox(u'发送返回信息:' + item['message'], u'邮件信息!', wx.OK|wx.ICON_INFORMATION)
                    if item['runtask'] == 'sendmail' and item['return']:
                        boxpanel = self.mailboxs['/%s/' % (name) + u'发件箱']

                        dbpath = os.path.join(config.cf.datadir, name, 'mailinfo.db')
                        conn = dbope.DBOpe(dbpath)
                        try:
                            ret = conn.query("select id,filename,subject,mailfrom,mailto,size,ctime,datetime(date,'unixepoch') as date,attach,mailbox,status from mailinfo where filename='%s'" % (item['filename']))
                        finally:
                            conn.close()
                    
                        if ret:
                            info = ret[0]
                            loginfo('get mail:', info['filename'])
                            att = 0 
                            loginfo('attach:', info['attach'])
                            if len(info['attach']) > 0:
                                att = 1
                            info['user'] = name
                            info['item'] = item['item']
                            info['box'] = '/%s/%s' % (name, info['mailbox'])
                            info['filepath'] = os.path.join(config.cf.datadir, name, info['mailbox'], info['filename'].lstrip(os.sep))
                        
                            loginfo('info:', info)
                            boxpanel.change_box(info, 'sendover') 

                elif task == 'status':
                    pass
                else:
                    logerr('uiq return error:', item)
        
    def OnFileOpen(self, event):
        dlg = wx.FileDialog(
            self, message=u"选择邮件",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=u"邮件文件 (*.eml)|*.eml",
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                loginfo('open mail:', path)
                
        dlg.Destroy()
        
    def OnFileSaveAs(self, event):
        item = self.tree.last_item_data()
        if not item:
            return
        user  = item['user']
        panel = item['panel']

        data = panel.get_item_data()
        loginfo('save data:', data)

        dlg = wx.FileDialog(
            self, message=u"保存邮件",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=u"邮件内容 (*.html)|*.html",
            style=wx.SAVE
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:
                info = mailparse.decode_mail(data['filepath'])
                if info['html']:
                    data = u'主　题: ' + info['subject'] + u'<br>发件人: ' + info['from'] + '<br><br>' + info['html']
                else:
                    data = u'主　题: ' + info['subject'] + u'<br>发件人: ' + info['from'] + '<br><br>' + info['plain'].replace('\n', '<br>')
                f = open(path, 'w')
                f.write(data.encode(mailparse.charset, 'ignore'))
                f.close()
        dlg.Destroy()

    def OnFileGetMail(self, event):
        data = self.tree.last_item_data()
        if not data:
            return
        loginfo('last_mailbox:', data['user'])
        x = {'name':data['user'], 'task':'recvmail'}
        config.taskq.put(x)
        
    def OnFileSendMail(self, event):
        self.file_send_mail()

    def file_send_mail(self, user=None):
        if not user:
            item = self.tree.last_item_data()
            if not item:
                return
            user  = item['user']
        path = '/' + user + u'/发件箱'
        panel = self.mailboxs[path]
        
        allnodes = [] 
        for node in panel.parent_items:
            child, cookie = panel.tree.GetFirstChild(node) 
            loginfo('first child:', child)
            allnodes.append(child)
            while True:
                child, cookie = panel.tree.GetNextChild(node, cookie) 
                loginfo('next child:', child)
                if not child:
                    break
                allnodes.append(child)
        loginfo('allnodes:', allnodes)        
        
        for node in allnodes:
            maildata = panel.tree.GetItemData(node).GetData()
            msg = {'name':user, 'task':'sendmail', 'to':[maildata['mailto']], 
               'from':maildata['mailfrom'], 'path':maildata['filepath'], 'item':node}
            config.taskq.put(msg)
        

    def OnFileGetAllMail(self, event):
        for k in config.cf.users:
            x = {'name':k, 'task':'recvmail'}
            config.taskq.put(x)
           

    def OnFileSendAllMail(self, event):
        for k in config.cf.users:
            self.file_send_mail(k)
        
    def OnFileImport(self, event):
        itemdata = self.tree.last_item_data()
        if not itemdata:
            return
        user  = itemdata['user']
        item = self.tree.last_item()
        
        dlg = wx.FileDialog(
            self, message=u"选择要导入的邮件, 必须是.eml文件",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=u"所有邮件文件 (*.eml)|*.eml",
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            loginfo('mail:', paths)
            #self.file_import(paths)
            for path in paths:
                utils.mail_import(user, itemdata, path)
        dlg.Destroy()

    def file_import(self, filename=None):
        if type(filename) == types.ListType:
            for fname in filename:
                f = open(fname, 'r')
                f.close()
        else:
            f = open(filename)
            f.close()
    
    def OnFileExport(self, event):
        item = self.tree.last_item_data()
        if not item:
            return
        user  = item['user']
        panel = item['panel']

        data = panel.get_item_data()
        loginfo('save data:', data)

        dlg = wx.FileDialog(
            self, message=u"保存导出邮件",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=u"邮件文件 (*.eml)|*.eml",
            style=wx.SAVE
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:
                fr = open(data['filepath'], 'r')
                s = fr.read()
                fr.close()
                
                fw = open(path, 'w')
                fw.write(s)
                fw.close()
        dlg.Destroy()
        
    def OnFileExit(self, event):
        self.Hide()
        self.mgr.UnInit()
        del self.mgr
        self.Destroy()
        sys.exit()
            
    def OnViewMail(self, event):
        self.mgr.GetPane('listcnt').Show()
        self.mgr.Update()

    def OnViewAttach(self, event):
        self.mgr.GetPane('attachctl').Show()
        self.mgr.Update()
       
    def OnViewContact(self, event):
        self.mgr.GetPane('contact').Show()
        self.mgr.Update()
 
    def OnViewSource(self, event):
        self.mailboxs[self.last_mailbox].OnPopupSource(event)
    
    def OnViewEncode(self, event):
        pass
        
    def OnImportOutlookUser(self, event):
        pass       
    def OnImportOutlookMailbox(self, event):
        pass
    def OnImportOutlookLinkman(self, event):
        pass
    def OnImportFoxmailUser(self, event):
        pass
    def OnImportFoxmailMailbox(self, event):
        pass
    def OnImportFoxmailLinkman(self, event):
        pass
    def OnImportCuteUser(self, event):
        pass
    def OnImportCuteMailbox(self, event):
        pass
    def OnImportCuteLinkman(self, event):
        pass
        
        
    def OnExportCuteUser(self, event):
        pass
    def OnExportCuteMailbox(self, event):
        pass
    def OnExportCuteLinkman(self, event):
        pass
        
        
    def OnViewTemplate(self, event):
        pass
    
    def OnMailboxUserNew(self, event):
        import images
        wizard = wiz.Wizard(self, -1, u"新建用户向导", images.WizTest1.GetBitmap())

        page1 = useradd.UsernamePage(wizard, u"输入用户信息")
        #page2 = useradd.EmailPage(wizard, u"输入邮件地址")
        page2 = useradd.ServerPage(wizard, u"输入服务器信息")
    
        wizard.FitToPage(page1)
    
        wiz.WizardPageSimple_Chain(page1, page2)
        #wiz.WizardPageSimple_Chain(page2, page3)
    
        wizard.GetPageAreaSizer().Add(page1)
        ret = wizard.RunWizard(page1)
        if ret:
            me = {'name': page1.boxname.GetValue(),
                  #'storage': page1.storage.GetValue(),
                  'storage':'',
                  'mailname': page1.username.GetValue(),
                  'email': page1.email.GetValue(),
                  'pop3_server': page2.pop3server.GetValue(),
                  'pop3_pass': page2.pop3pass.GetValue(),
                  'smtp_server': page2.smtpserver.GetValue(),
                  'smtp_pass': page2.smtppass.GetValue(),
                  }
            loginfo('me:', me)
            try:
                conf = config.cf.user_add(me)
            except Exception, e:
                wx.MessageBox(u"用户添加失败!"+str(e), u"欢迎使用CuteMail")
            else:
                #wx.MessageBox(u"用户添加成功!", u"欢迎使用CuteMail")
                self.tree.append(conf['mailbox'], me['name'])
                self.tree.Refresh()
                
        
    def OnMailboxUserRename(self, event):
        dlg = wx.TextEntryDialog(
                self, u'请输入新的账户名',
                u'修改账户名', 'Python')

        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()

        dlg.Destroy()
         
    def OnMailboxUserDel(self, event):
        dlg = wx.MessageDialog(self, u"用户删除将不能恢复! 点击 确定 同意删除，否则点击 取消", 
                u"确认要删除账户？", wx.YES_NO)
        if dlg.ShowModal() == wx.ID_OK:
            loginfo('mailbox user del choose ok.')
        dlg.Destroy()
        
        
    def OnMailboxUserOptions(self, event):
        self.tree.popup_setting()
        
    def OnMailWrite(self, event):
        data = self.tree.last_item_data()
        if not data:
            return
        user = data['user']
        loginfo('user name:', user)
        mailaddr = config.cf.users[user]['email']
        maildata = dict(zip(self.mail_writer_item, ['']*len(self.mail_writer_item)))
        maildata['from'] = mailaddr
        maildata['user'] = user
        maildata['attach'] = []
        #maildata = {'subject':'', 'from':mailaddr, 'to':'', 'text':'', 'user':user, 'attach':[]}


        frame = writer.WriterFrame(self, self.rundir, maildata)
        frame.Show(True)

    def OnMailReply(self, event):
        data = self.tree.last_item_data()
        if not data:
            return
        user = data['user']
        panel = data['panel']
       
        try:
            info = panel.get_item_content()
        except Exception, e:
            logerr('get_item_content error:', str(e))
        
        mailaddr = config.cf.users[user]['email']
        text = info['plain']
        text = text.replace('\r\n', '\n')
        parts = text.split('\n')
        for i in xrange(0, len(parts)):
            parts[i] = ">>" + parts[i]
        text = '\r\n'.join(parts)
        maildata = {'subject':'Re: '+info['subject'][:32], 'from':mailaddr, 'to':info['mailfrom'],
                    'text': text, 'user':user, 'attach':[]}
        #print 'reply:', maildata 
        frame = writer.WriterFrame(self, self.rundir, maildata)
        frame.Show(True)

    def OnMailReplyAll(self, event):
        data = self.tree.last_item_data()
        if not data:
            return
        user  = data['user']
        panel = data['panel']

        try:
            info = panel.get_item_content()
        except Exception, e:
            logerr('get_item_content error:', str(e))
           
        mailaddr = config.cf.users[user]['email']
        #maildata = {'subject':'Re: '+info['subject'][:32], 'from':mailaddr, 'to':'', 
        #            'text':info['plain'], 'user':user, 'attach':[]}
        
        maildata = dict(zip(self.mail_writer_item, ['']*len(self.mail_writer_item)))
        maildata['subject'] = 'Re: ' + info['subject'][:32]
        maildata['from'] = mailaddr
        maildata['user'] = user
        maildata['text'] = info['plain']
        maildata['attach'] = []
 
        frame = writer.WriterFrame(self, self.rundir, maildata)
        frame.Show(True)

    def OnMailForward(self, event):
        data = self.tree.last_item_data()
        if not data:
            return
        user  = data['user']
        panel = data['panel']

        try:
            info = panel.get_item_content()
        except Exception, e:
            logerr('get_item_content error:', str(e))
        
        mailaddr = config.cf.users[user]['email']
        #maildata = {'subject':'Fw:'+info['subject'][:32], 'from':mailaddr, 'to':'', 
        #            'text':info['plain'], 'user':user, 'attach':[]}
        attachs = [] 
        maildata = dict(zip(self.mail_writer_item, ['']*len(self.mail_writer_item)))
        maildata['subject'] = 'Fw: ' + info['subject'][:32]
        maildata['from'] = mailaddr
        maildata['user'] = user
        maildata['text'] = info['plain']
        maildata['attach'] = attachs
 
        frame = writer.WriterFrame(self, self.rundir, maildata)
        frame.Show(True)

    def OnMailSendSec(self, event):
        data = self.tree.last_item_data()
        if not data:
            wx.MessageBox(u"再次发送邮件失败！无法获取到当前邮件箱。", u"再次发送邮件")
            return
        user  = data['user']
        panel = data['panel']

        try:
            info = panel.get_item_content()
        except Exception, e:
            logerr('get_item_content error:', str(e))
        mailaddr = config.cf.users[user]['email']
        maildata = {'subject':info['subject'], 'from':mailaddr, 'to':info['mailto'], 
                    'text':info['plain'], 'user':user, 'attach':[]}
 
        frame = writer.WriterFrame(self, self.rundir, maildata)
        frame.Show(True)

    def OnMailAttach(self, event):
        data = self.tree.last_item_data()
        if not data:
            wx.MessageBox(u"作为附件发送邮件失败！无法获取到当前邮件箱。", u"再次发送邮件")
            return
        user  = data['user']
        panel = data['panel']

        try:
            info = panel.get_item_content()
        except Exception, e:
            logerr('get_item_content error:', str(e))
        mailaddr = config.cf.users[user]['email']
        maildata = {'subject':info['subject'], 'from':mailaddr, 'to':info['mailto'], 
                    'text':info['plain'], 'user':user, 'attach':[]}
 
        frame = writer.WriterFrame(self, self.rundir, maildata)
        frame.Show(True)



    def OnMailSelectAll(self, event):
        data = self.tree.last_item_data()
        if not data:
            wx.MessageBox(u"选择邮件失败！无法获取到当前邮件箱。", u"选择所有邮件")
            return
        user  = data['user']
        panel = data['panel']

        panel.select_all_items()

    def OnMailCopyTo(self, event):
        pass
    def OnMailMoveTo(self, event):
        pass

    def OnMailDel(self, event):
        loginfo('delete mail')
        if self.last_mailbox == '/':
            return
        
        panel = self.mailboxs[self.last_mailbox]
        if not panel:
            return
        
        panel.change_last_box('trash')

    def OnMailFlag(self, event):
        pass
    
    #def OnMailSearch(self, event):
    #    pass

    def OnMailboxNew(self, event):
        self.tree.last_item_add_child()
        
    def OnMailboxRename(self, event):
        self.tree.last_item_rename() 
        
    def OnMailboxDel(self, event):
        self.tree.last_item_remove()
       
    def OnMailboxClearTrash(self, event):
        wx.MessageBox(u"清除已删除邮件完成!", u"清除已删除邮件")
    
    def OnMailboxClearSpam(self, event):
        wx.MessageBox(u"清除垃圾邮件完成!", u"清除垃圾邮件")
        
    def OnHelp(self, event):
        wx.MessageBox(u"暂时没有帮助信息!", u"帮助信息")
        
    def OnHelpUpdate(self, event):
        wx.MessageBox(u"没有可用更新!", u"检查更新")
    
    def OnHelpAbout(self, event):
        info = wx.AboutDialogInfo()
        info.Name = u"CuteMail"
        info.Version = "0.8.0"
        info.Copyright = "(C) 2009 zhaoweikid"
        info.Description = wordwrap(
            "CuteMail is a opensource mail client write by Python language.\n"
            "You will run this on WindowsXP or Linux or MacOS X.\n"
            "It used wxPython\n",
            350, wx.ClientDC(self))
        info.WebSite = ("http://code.google.com/p/cutemail", "CuteMail home page")
        info.Developers = [ "zhaoweikid",
                            "lanwenhong"]

        info.License = wordwrap("GPL", 500, wx.ClientDC(self))
        wx.AboutBox(info)

    def OnWebsite(self, event):
        self.display_mailbox(u'/')
        
        
        
