#!/usr/bin/python
# coding: utf-8
import os, sys, cStringIO, string, time
import wx
import wx.aui
import wx.wizard as wiz
import wx.lib.sized_controls as sc
from   picmenu import PicMenu
from   listindex import *
import treelist, viewhtml
import config, common, dbope, useradd
import writer
import cPickle as pickle
import pop3

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
        # 为面板管理器增加用户邮箱树形结构
        self.mgr.AddPane(self.tree, wx.aui.AuiPaneInfo().Name("tree").Caption(u"用户").
                          Left().Layer(1).Position(1).CloseButton(True).MaximizeButton(True))
            
        # 把邮件内容面板添加到面板管理器
        self.mgr.AddPane(self.listcnt, wx.aui.AuiPaneInfo().Name("listcnt").Caption(u"邮件内容").
                          Bottom().Layer(0).Position(3).CloseButton(True).MaximizeButton(True))
        
        self.mgr.AddPane(self.attachctl, wx.aui.AuiPaneInfo().Name("attachctl").Caption(u"附件内容").
                          Bottom().Layer(0).Position(4).CloseButton(True).MaximizeButton(True))
        # 显示当前选择的邮件列表面板
        print 'show:', self.last_mailbox
        self.mgr.GetPane(self.last_mailbox).Show()
        self.mgr.Update()
        
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer = wx.Timer(self)
        self.timer.Start(1000)
        
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
    def add_mailbox_panel(self, k, obj=None):
        print 'add panel:', k
        if not obj:
            obj = treelist.MailListPanel(self, k)
        obj.Hide()
        self.mailboxs[k] = obj
        self.mgr.AddPane(obj, wx.aui.AuiPaneInfo().Name(k).CenterPane().Hide())
        return obj
        
        
    def init_data(self):
        mailboxkeys = self.mailboxs.keys()
        for k in mailboxkeys:
            print 'init data:', k
            if not self.mailboxs[k]:
                self.add_mailbox_panel(k)
        k = u'/'
        obj = viewhtml.ViewHtml(self)
        obj.set_url('http://www.pythonid.com')
        self.add_mailbox_panel(k, obj)
        
    def load_db_one(self, user, mid):
        dbpath = os.path.join(config.cf.datadir, user, 'mailinfo.db')
        print 'load db from path:', dbpath
        conn = dbope.DBOpe(dbpath)
        ret = conn.query("select id,filename,subject,mailfrom,mailto,size,ctime,date,attach,mailbox,status from mailinfo where id=" + str(mid))
        conn.close()
        for row in ret:
            att = 0
            if row['attach']:
                att = 1
                
            boxname = '/%s/' % (user) + config.cf.mailbox_map_en2cn[row['mailbox']]
            row['user'] = user
            row['box'] = boxname
            row['filepath'] = os.path.join(config.cf.datadir, user, row['mailbox'], row['filename'].lstrip(os.sep))

            mailaddr = row['mailfrom']
            if row['mailbox'] in ['send','draft','sendover']:
                mailaddr = row['mailto']
            item = [mailaddr, att, 0, row['subject'], row['date'], str(row['size']/1024 + 1)+' K',
                    wx.TreeItemData(row)]
                #print item
            panel = self.mailboxs[boxname]
            panel.add_mail(item)
            
    def load_db_data(self):
        users = config.cf.users
        for u in users:
            #mlist = self.mailboxs['/%s/' % (u) + u'收件箱']
            dbpath = os.path.join(config.cf.datadir, u, 'mailinfo.db')
            print 'load db from path:', dbpath
            conn = dbope.DBOpe(dbpath)
            ret = conn.query("select id,filename,subject,mailfrom,mailto,size,ctime,date,attach,mailbox,status from mailinfo order by date")
            conn.close()
            for row in ret:
                att = 0
                if row['attach']:
                    att = 1
                    
                boxname = '/%s/' % (u) + config.cf.mailbox_map_en2cn[row['mailbox']]
                row['user'] = u
                row['box'] = boxname
                row['filepath'] = os.path.join(config.cf.datadir, u, row['mailbox'], row['filename'].lstrip(os.sep))

                mailaddr = row['mailfrom']
                if row['mailbox'] in ['send','draft','sendover']:
                    mailaddr = row['mailto']
 
                item = [mailaddr, att, 0, row['subject'], row['date'], str(row['size']/1024 + 1)+' K',
                        wx.TreeItemData(row)]
                #print item
                panel = self.mailboxs[boxname]
                panel.add_mail(item)

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
        self.ID_VIEW_SMTP    = wx.NewId()
        self.ID_VIEW_SEARCH  = wx.NewId()
        self.ID_VIEW_ENCODE  = wx.NewId()
        self.ID_VIEW_SORT    = wx.NewId()
        self.ID_VIEW_REFRESH = wx.NewId()
        self.ID_VIEW_SOURCE  = wx.NewId()
        
        self.ID_TOOL_LINKMAN    = wx.NewId()
        self.ID_TOOL_NOTE       = wx.NewId()
        self.ID_TOOL_CHAT       = wx.NewId()
        self.ID_TOOL_TEMPLATE   = wx.NewId()
        self.ID_TOOL_IMPORT     = wx.NewId()
        self.ID_TOOL_EXPORT     = wx.NewId()
        self.ID_TOOL_SETTING    = wx.NewId()
        
        self.ID_MAIL_WRITE     = wx.NewId()
        self.ID_MAIL_REPLY     = wx.NewId()
        self.ID_MAIL_REPLY_ALL = wx.NewId()
        self.ID_MAIL_FORWARD   = wx.NewId()
        self.ID_MAIL_SEND_SEC  = wx.NewId()
        self.ID_MAIL_ATTACH    = wx.NewId()
       
        self.ID_MAIL_ADD_WHITE = wx.NewId()
        self.ID_MAIL_ADD_BLACK = wx.NewId()

        self.ID_MAIL_SELECTALL = wx.NewId()
        self.ID_MAIL_COPYTO    = wx.NewId()
        self.ID_MAIL_MOVETO    = wx.NewId()
        self.ID_MAIL_DEL       = wx.NewId()
        self.ID_MAIL_FLAG      = wx.NewId()
        self.ID_MAIL_SEARCH    = wx.NewId()
        self.ID_MAIL_OPTIONS   = wx.NewId()
 
        self.ID_MAILBOX_USER_NEW            = wx.NewId()
        self.ID_MAILBOX_USER_RENAME         = wx.NewId()
        self.ID_MAILBOX_USER_DEL            = wx.NewId()
        self.ID_MAILBOX_USER_FILTER_SETTING = wx.NewId()
        self.ID_MAILBOX_USER_BWLIST_SETTING = wx.NewId()
        self.ID_MAILBOX_USER_OPTIONS        = wx.NewId()
       
        self.ID_MAILBOX_NEW         = wx.NewId()
        self.ID_MAILBOX_RENAME      = wx.NewId()
        self.ID_MAILBOX_DEL         = wx.NewId()
        self.ID_MAILBOX_CLEAR_TRASH = wx.NewId()
        self.ID_MAILBOX_CLEAR_SPAM  = wx.NewId()
        
        self.ID_HELP          = wx.NewId()
        self.ID_HELP_FEEDBACK = wx.NewId()
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
        self.ID_TOOLBAR_FIND = wx.NewId()
        self.ID_TOOLBAR_WWW = wx.NewId()
        self.ID_TOOLBAR_CHAT = wx.NewId()
        
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
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_ADDR, u'地址薄', common.load_bitmap('bitmaps/32/toggle_log.png'), shortHelp=u"地址薄", longHelp=u"地址薄")
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_FIND, u'查找', common.load_bitmap('bitmaps/32/filefind.png'), shortHelp=u"查找", longHelp=u"查找")
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_CHAT, u'聊天', common.load_bitmap('bitmaps/32/chat.png'), shortHelp=u"聊天", longHelp=u"聊天")
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_WWW, u'主页', common.load_bitmap('bitmaps/32/home.png'), shortHelp=u"主页", longHelp=u"主页")
        self.toolbar.Realize ()
        self.SetToolBar(self.toolbar)
        
        self.Bind(wx.EVT_TOOL, self.OnFileGetMail, id=self.ID_TOOLBAR_MAIL_GET)
        self.Bind(wx.EVT_TOOL, self.OnFileSendMail, id=self.ID_TOOLBAR_MAIL_SEND)
        self.Bind(wx.EVT_TOOL, self.OnMailWrite, id=self.ID_TOOLBAR_MAIL_NEW)
        self.Bind(wx.EVT_TOOL, self.OnMailReply, id=self.ID_TOOLBAR_MAIL_REPLY)
        self.Bind(wx.EVT_TOOL, self.OnMailForward, id=self.ID_TOOLBAR_MAIL_FORWARD)
        self.Bind(wx.EVT_TOOL, self.OnMailDel, id=self.ID_TOOLBAR_MAIL_DELETE)
        self.Bind(wx.EVT_TOOL, self.OnToolLinkman, id=self.ID_TOOLBAR_ADDR)
        self.Bind(wx.EVT_TOOL, self.OnMailSearch, id=self.ID_TOOLBAR_FIND)
        self.Bind(wx.EVT_TOOL, self.OnToolChat, id=self.ID_TOOLBAR_CHAT)
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
        self.viewmenu.Append(self.ID_VIEW_MAIL, u"邮件内容", 'contents.png')        
        self.viewmenu.Append(self.ID_VIEW_ATTACH, u"附件内容", 'attach.png')        
        self.viewmenu.Append(self.ID_VIEW_SMTP, u"调试信息", 'blender.png')
        self.viewmenu.Append(self.ID_VIEW_SOURCE, u"信件原文", 'note.png')
        self.viewmenu.Append(self.ID_VIEW_SEARCH, u"查找邮件", 'mail_find.png')
        self.viewmenu.AppendSeparator()
        self.viewmenu.AppendMenu(self.ID_VIEW_ENCODE, u"编码", encodingmenu)
        #self.viewmenu.Append(self.ID_VIEW_SORT, "排序", None)
        self.viewmenu.Append(self.ID_VIEW_REFRESH, u"刷新", 'refresh.png')        

        importmenu = wx.Menu()
        importmenu.Append(self.ID_IMPORT_MAB_USER, u"导入cutemail帐户")
        importmenu.Append(self.ID_IMPORT_MAB_MAILBOX, u"导入cutemail邮箱")
        importmenu.Append(self.ID_IMPORT_MAB_LINKMAN, u"导入cutemail地址薄")
        importmenu.AppendSeparator()
        importmenu.Append(self.ID_IMPORT_OUTLOOK_USER, u"导入outlook帐户")
        importmenu.Append(self.ID_IMPORT_OUTLOOK_MAILBOX, u"导入outlook邮箱")
        importmenu.Append(self.ID_IMPORT_OUTLOOK_LINKMAN, u"导入outlook地址薄")
        importmenu.AppendSeparator()
        importmenu.Append(self.ID_IMPORT_FOXMAIL_USER, u"导入foxmail帐户")
        importmenu.Append(self.ID_IMPORT_FOXMAIL_MAILBOX, u"导入foxmail邮箱")
        importmenu.Append(self.ID_IMPORT_FOXMAIL_LINKMAN, u"导入foxmail地址薄")
        
        exportmenu = wx.Menu()        
        exportmenu.Append(self.ID_EXPORT_MAB_USER, u"导出cutemail帐户")
        exportmenu.Append(self.ID_EXPORT_MAB_MAILBOX, u"导出cutemail邮箱")
        exportmenu.Append(self.ID_EXPORT_MAB_LINKMAN, u"导出cutemail地址薄")
        
        self.toolmenu = PicMenu(self)
        self.toolmenu.Append(self.ID_TOOL_LINKMAN, u"地址薄", 'note.png')
        self.toolmenu.Append(self.ID_TOOL_NOTE, u"日历提醒", 'alarm.png')
        self.toolmenu.Append(self.ID_TOOL_CHAT, u"聊天", 'filetypes.png')
        self.toolmenu.Append(self.ID_TOOL_TEMPLATE, u"模板管理", "template.png")
       
        self.toolmenu.AppendSeparator()
        self.toolmenu.AppendMenu(self.ID_TOOL_IMPORT, u"导入", importmenu)
        self.toolmenu.AppendMenu(self.ID_TOOL_EXPORT, u"导出", exportmenu)
        self.toolmenu.AppendSeparator()
        self.toolmenu.Append(self.ID_TOOL_SETTING, u"设置", 'preferences.png')
        
        self.mailmenu = PicMenu(self)
        self.mailmenu.Append(self.ID_MAIL_WRITE, u"写新邮件", 'mail_new.png')
        self.mailmenu.Append(self.ID_MAIL_REPLY, u"回复邮件", 'mail_reply.png')
        self.mailmenu.Append(self.ID_MAIL_REPLY_ALL, u"回复全部", 'mail_replyall.png')
        self.mailmenu.Append(self.ID_MAIL_FORWARD, u"转发邮件", 'mail_send.png')            
        self.mailmenu.Append(self.ID_MAIL_SEND_SEC, u"再次发送", 'mail_send.png')
        self.mailmenu.Append(self.ID_MAIL_ATTACH, u"作为附件发送", 'mail_send.png')
        self.mailmenu.AppendSeparator()
        
        self.mailmenu.Append(self.ID_MAIL_ADD_WHITE, u"添加发信人到白名单")
        self.mailmenu.Append(self.ID_MAIL_ADD_BLACK, u"添加发信人到黑名单")
        self.mailmenu.AppendSeparator()
        self.mailmenu.Append(self.ID_MAIL_SELECTALL, u"选择所有", 'check.png')
        self.mailmenu.Append(self.ID_MAIL_COPYTO, u"复制到", 'editcopy.png')
        self.mailmenu.Append(self.ID_MAIL_MOVETO, u"移动到", 'editcut.png')
        self.mailmenu.Append(self.ID_MAIL_DEL, u"删除", 'editdelete.png')
        self.mailmenu.AppendSeparator()
        self.mailmenu.Append(self.ID_MAIL_FLAG, u"标记为", 'flag.png')
        self.mailmenu.Append(self.ID_MAIL_SEARCH, u"查找", 'mail_find.png') 
        self.mailmenu.AppendSeparator()
        self.mailmenu.Append(self.ID_MAIL_OPTIONS, u"属性", 'preferences.png')
        
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

        self.mailboxmenu.AppendSeparator()
        self.mailboxmenu.Append(self.ID_MAILBOX_USER_BWLIST_SETTING, u"黑白名单")
        self.mailboxmenu.Append(self.ID_MAILBOX_USER_FILTER_SETTING, u"过滤器设置")
        
        self.mailboxmenu.AppendSeparator()
        self.mailboxmenu.Append(self.ID_MAILBOX_USER_OPTIONS, u"属性", 'preferences.png')       

        
        self.helpmenu = PicMenu(self)
        self.helpmenu.Append(self.ID_HELP, u"帮助主题", 'help.png')      
        self.helpmenu.AppendSeparator()
        self.helpmenu.Append(self.ID_HELP_FEEDBACK, u"反馈", 'help.png')        
        self.helpmenu.Append(self.ID_HELP_UPDATE, u"更新", 'help.png') 
        self.helpmenu.Append(self.ID_HELP_ABOUT, u"关于", 'info.png')
        
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.filemenu,u"文件")        
        self.menuBar.Append(self.viewmenu,u"查看")
        self.menuBar.Append(self.toolmenu,u"工具")
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
        self.Bind(wx.EVT_MENU, self.OnViewSmtp, id=self.ID_VIEW_SMTP)
        self.Bind(wx.EVT_MENU, self.OnViewSource, id=self.ID_VIEW_SOURCE)
        self.Bind(wx.EVT_MENU, self.OnViewSearch, id=self.ID_VIEW_SEARCH)
        self.Bind(wx.EVT_MENU, self.OnViewEncode, id=self.ID_VIEW_ENCODE)
        self.Bind(wx.EVT_MENU, self.OnViewSort, id=self.ID_VIEW_SORT)
        self.Bind(wx.EVT_MENU, self.OnViewRefresh, id=self.ID_VIEW_REFRESH)
        
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
        
        self.Bind(wx.EVT_MENU, self.OnToolLinkman, id=self.ID_TOOL_LINKMAN)
        self.Bind(wx.EVT_MENU, self.OnToolNote, id=self.ID_TOOL_NOTE)
        self.Bind(wx.EVT_MENU, self.OnToolTemplate, id=self.ID_TOOL_TEMPLATE)
        self.Bind(wx.EVT_MENU, self.OnToolImport, id=self.ID_TOOL_IMPORT)
        self.Bind(wx.EVT_MENU, self.OnToolExport, id=self.ID_TOOL_EXPORT)
        self.Bind(wx.EVT_MENU, self.OnToolSetting, id=self.ID_TOOL_SETTING)
        
        self.Bind(wx.EVT_MENU, self.OnMailboxUserNew, id=self.ID_MAILBOX_USER_NEW)
        self.Bind(wx.EVT_MENU, self.OnMailboxUserRename, id=self.ID_MAILBOX_USER_RENAME)
        self.Bind(wx.EVT_MENU, self.OnMailboxUserDel, id=self.ID_MAILBOX_USER_DEL)
        self.Bind(wx.EVT_MENU, self.OnMailboxUserBWListSetting, id=self.ID_MAILBOX_USER_BWLIST_SETTING)
        self.Bind(wx.EVT_MENU, self.OnMailboxUserFilterSetting, id=self.ID_MAILBOX_USER_FILTER_SETTING)
        self.Bind(wx.EVT_MENU, self.OnMailboxUserOptions, id=self.ID_MAILBOX_USER_OPTIONS)
        
        self.Bind(wx.EVT_MENU, self.OnMailWrite, id=self.ID_MAIL_WRITE)
        self.Bind(wx.EVT_MENU, self.OnMailReply, id=self.ID_MAIL_REPLY)
        self.Bind(wx.EVT_MENU, self.OnMailReplyAll, id=self.ID_MAIL_REPLY_ALL)
        self.Bind(wx.EVT_MENU, self.OnMailForward, id=self.ID_MAIL_FORWARD)
        self.Bind(wx.EVT_MENU, self.OnMailSendSec, id=self.ID_MAIL_SEND_SEC)
        self.Bind(wx.EVT_MENU, self.OnMailAttach, id=self.ID_MAIL_ATTACH)
        self.Bind(wx.EVT_MENU, self.OnMailAddWhite, id=self.ID_MAIL_ADD_WHITE)
        self.Bind(wx.EVT_MENU, self.OnMailAddBlack, id=self.ID_MAIL_ADD_BLACK)
        self.Bind(wx.EVT_MENU, self.OnMailSelectAll, id=self.ID_MAIL_SELECTALL)
        self.Bind(wx.EVT_MENU, self.OnMailCopyTo, id=self.ID_MAIL_COPYTO)
        self.Bind(wx.EVT_MENU, self.OnMailMoveTo, id=self.ID_MAIL_MOVETO)
        self.Bind(wx.EVT_MENU, self.OnMailDel, id=self.ID_MAIL_DEL)
        self.Bind(wx.EVT_MENU, self.OnMailFlag, id=self.ID_MAIL_FLAG)
        self.Bind(wx.EVT_MENU, self.OnMailSearch, id=self.ID_MAIL_SEARCH)
        self.Bind(wx.EVT_MENU, self.OnMailOptions, id=self.ID_MAIL_OPTIONS)
        
        self.Bind(wx.EVT_MENU, self.OnMailboxNew, id=self.ID_MAILBOX_NEW)
        self.Bind(wx.EVT_MENU, self.OnMailboxRename, id=self.ID_MAILBOX_RENAME)
        self.Bind(wx.EVT_MENU, self.OnMailboxDel, id=self.ID_MAILBOX_DEL)
        self.Bind(wx.EVT_MENU, self.OnMailboxClearTrash, id=self.ID_MAILBOX_CLEAR_TRASH)
        self.Bind(wx.EVT_MENU, self.OnMailboxClearSpam, id=self.ID_MAILBOX_CLEAR_SPAM)


        self.Bind(wx.EVT_MENU, self.OnHelp, id=self.ID_HELP)
        self.Bind(wx.EVT_MENU, self.OnHelpFeedback, id=self.ID_HELP_FEEDBACK)
        self.Bind(wx.EVT_MENU, self.OnHelpUpdate, id=self.ID_HELP_UPDATE)
        self.Bind(wx.EVT_MENU, self.OnHelpAbout, id=self.ID_HELP_ABOUT)
        
    def make_statusbar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.SetStatusWidths([-1, -2, -2])
        
    def display_mailbox(self, name):
        print 'display name:', name
        try:
            newobj = self.mailboxs[name]
        except Exception, e:
            print e
            return False
        
        print 'display:', self.last_mailbox, name
        
        try:
            if self.last_mailbox:
                self.mgr.GetPane(self.last_mailbox).Hide()
            self.mgr.GetPane(name).Show()
            self.mgr.Update()
            self.last_mailbox = name       
        except Exception, e:
            print 'display_mailbox:', e
        return True
        
        
    def OnCloseWindow(self, event):
        self.Hide()
        self.mgr.UnInit()
        del self.mgr
        self.Destroy()

    def OnSize(self, event):
        self.Refresh()
            
    def OnTimer(self, event):
        '''
        定时任务
        '''
        #print 'time now', time.ctime()
        try:
            item = config.uiq.get(0)
        except:
            pass
        else:
            print 'uiq: ', item
            name = item['name']
            task = item['task']
            boxpanel = self.mailboxs['/%s/' % (name) + u'收件箱']
            if task == 'updatebox':
                usercf = config.cf.users[name]
                dbpath = os.path.join(config.cf.datadir, name, 'mailinfo.db')
                conn = dbope.DBOpe(dbpath)
                ret = conn.query("select id,filename,subject,mailfrom,mailto,size,ctime,date,attach,mailbox,status from mailinfo where status='new'")
                conn.close()
                if ret:
                    for info in ret:
                        print info['filename']
                        att = 0 
                        if info['attach']:
                            att = 1
                        info['user'] = name
                        info['box'] = '/%s/%s' % (name, info['mailbox'])
                        info['filepath'] = os.path.join(config.cf.datadir, name, info['mailbox'], info['filename'].lstrip(os.sep))
                        item = [info['mailfrom'], att,1, info['subject'], info['date'], str(info['size']/1024 + 1)+' K',
                                wx.TreeItemData(info)]
                        #print item
                        boxpanel.add_mail(item)
                        #mlist.add_item(item, mlist.today)
            elif task == 'alert':
                wx.MessageBox(u'发送返回信息:' + item['message'], u'邮件信息!', wx.OK|wx.ICON_ERROR)
            elif task == 'status':
                pass
            else:
                print 'uiq return error:', item
        
    def OnFileOpen(self, event):
        pass 

    def OnFileSaveAs(self, event):
        pass
    def OnFileGetMail(self, event):
        data = self.tree.last_item_data()
        if not data:
            return
        print 'last_mailbox:', data['user']
        x = {'name':data['user'], 'task':'recvmail'}
        config.taskq.put(x)
        
    def OnFileSendMail(self, event):
        pass
    def OnFileGetAllMail(self, event):
        pass
    def OnFileSendAllMail(self, event):
        pass
    def OnFileImport(self, event):
        pass
    def OnFileExport(self, event):
        pass
    def OnFileExit(self, event):
        self.Hide()
        self.mgr.UnInit()
        del self.mgr
        self.Destroy()
            
    def OnViewMail(self, event):
        self.mgr.GetPane('listcnt').Show()
        self.mgr.Update()

    def OnViewAttach(self, event):
        self.mgr.GetPane('attachctl').Show()
        self.mgr.Update()
        
    def OnViewSmtp(self, event):
        pass
        
    def OnViewSource(self, event):
        self.mailboxs[self.last_mailbox].OnPopupSource(event)
    
    def OnViewSearch(self, event):
        pass
    def OnViewEncode(self, event):
        pass
    def OnViewSort(self, event):
        pass
    def OnViewRefresh(self, event):
        self.Refresh()
        
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
        
        
    def OnToolLinkman(self, event):
        pass
    def OnToolNote(self, event):
        pass
    def OnToolChat(self, event):
        pass
    def OnToolTemplate(self, event):
        pass
    def OnToolImport(self, event):
        pass
    def OnToolExport(self, event):
        pass
    def OnToolSetting(self, event):
        pass
        
        
    def OnMailboxUserNew(self, event):
        import images
        print 'run simple wizard...'
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
                  'smtp_server:': page2.smtpserver.GetValue(),
                  'smtp_pass': page2.smtppass.GetValue(),
                  }
            print 'me:', me
            try:
                conf = config.cf.user_add(me)
            except Exception, e:
                wx.MessageBox(u"用户添加失败!"+str(e), u"欢迎使用CuteMail")
            else:
                #wx.MessageBox(u"用户添加成功!", u"欢迎使用CuteMail")
                self.tree.append(conf['mailbox'], me)
                self.tree.Refresh()
                
        
    def OnMailboxUserRename(self, event):
        pass
    def OnMailboxUserDel(self, event):
        pass
    def OnMailboxUserBWListSetting(self, event):
        pass
    def OnMailboxUserFilterSetting(self, event):
        pass
    def OnMailboxUserOptions(self, event):
        pass
        
    def OnMailWrite(self, event):
        data = self.tree.last_item_data()
        if not data:
            return
        user = data['user']
        print 'user name:', user
        mailaddr = config.cf.users[user]['email']
        maildata = {'subject':'', 'from':mailaddr, 'to':'', 'text':'', 'user':user}

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
            print 'get_item_content error:', str(e)
        
        mailaddr = config.cf.users[user]['email']
        text = info['plain']
        text = text.replace('\r\n', '\n')
        parts = text.split('\n')
        for i in xrange(0, len(parts)):
            parts[i] = ">>" + parts[i]
        text = '\r\n'.join(parts)
        maildata = {'subject':'Re: '+info['subject'][:32], 'from':mailaddr, 'to':info['mailfrom'],
                    'text': text, 'user':user}
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
            print 'get_item_content error:', str(e)
           
        mailaddr = config.cf.users[user]['email']
        maildata = {'subject':'Re: '+info['subject'][:32], 'from':mailaddr, 'to':'', 
                    'text':info['plain'], 'user':user}
 
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
            print 'get_item_content error:', str(e)
        
        mailaddr = config.cf.users[user]['email']
        maildata = {'subject':'Fw:'+info['subject'][:32], 'from':mailaddr, 'to':'', 
                    'text':info['plain'], 'user':user}
        frame = writer.WriterFrame(self, self.rundir, maildata)
        frame.Show(True)

    def OnMailSendSec(self, event):
        data = self.tree.last_item_data()
        if not data:
            return
        user  = data['user']
        panel = data['panel']

        try:
            info = panel.get_item_content()
        except Exception, e:
            print 'get_item_content error:', str(e)
        mailaddr = config.cf.users[user]['email']
        maildata = {'subject':info['subject'], 'from':mailaddr, 'to':info['mailto'], 
                    'text':info['plain'], 'user':user}
 
        frame = writer.WriterFrame(self, self.rundir, maildata)
        frame.Show(True)

    def OnMailAttach(self, event):
        pass
    def OnMailAddWhite(self, event):
        pass
    def OnMailAddBlack(self, event):
        pass
    def OnMailSelectAll(self, event):
        pass
    def OnMailCopyTo(self, event):
        pass
    def OnMailMoveTo(self, event):
        pass
    def OnMailDel(self, event):
        print 'delete mail'
        if self.last_mailbox == '/':
            return
        
        panel = self.mailboxs[self.last_mailbox]
        if not panel:
            return
        
        panel.change_box('trash')

    def OnMailFlag(self, event):
        pass
    def OnMailSearch(self, event):
        pass
    def OnMailOptions(self, event):
        pass    
        
        
    def OnMailboxNew(self, event):
        self.tree.last_item_add_child()
        
    def OnMailboxRename(self, event):
        self.tree.last_item_rename() 
        
    def OnMailboxDel(self, event):
        self.tree.last_item_remove()
       
    def OnMailboxClearTrash(self, event):
        pass
    def OnMailboxClearSpam(self, event):
        pass
        
    def OnHelp(self, event):
        pass
    def OnHelpFeedback(self, event):
        pass
    def OnHelpUpdate(self, event):
        pass
    def OnHelpAbout(self, event):
        pass


    def OnWebsite(self, event):
        self.display_mailbox(u'/')
        
        
        
