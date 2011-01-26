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
import config, dbope, useradd, logfile, uiconfig
import writer, userbox, search
import cPickle as pickle
import pop3, mailparse, utils
from common import load_bitmap
from logfile import loginfo, logerr, logwarn

class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(1100, 700), 
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
        
        self.mgr.AddPane(self.contact, wx.aui.AuiPaneInfo().
                    Name("contact").Caption(u"联系人").
                    Right().Layer(0).Position(2).CloseButton(True).MaximizeButton(False))
        self.mgr.GetPane('contact').Hide()

        # 为面板管理器增加用户邮箱树形结构
        self.mgr.AddPane(self.tree, wx.aui.AuiPaneInfo().Name("tree").Caption(u"用户").
                          Left().Layer(1).Position(1).CloseButton(False).
                          MaximizeButton(False))
            
        # 把邮件内容面板添加到面板管理器
        self.mgr.AddPane(self.listcnt, wx.aui.AuiPaneInfo().
                          Name("listcnt").Caption(u"邮件内容").
                          MinSize(wx.Size(-1, 200)).
                          Bottom().Layer(0).Position(1).CloseButton(True).
                          MaximizeButton(True))
        
        self.mgr.AddPane(self.attachctl, wx.aui.AuiPaneInfo().
                         Name("attachctl").Caption(u"附件内容").
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

    def make_toolbar(self):
        self.toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.Size(48, 48), wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_TEXT)
        self.toolbar.SetToolBitmapSize(wx.Size (48, 48))
        
        for tb in uiconfig.toolbar:            
            if type(tb) != type([]):
                self.toolbar.AddSeparator()
                continue 
            setattr(self, tb[1], tb[0])
            self.toolbar.AddLabelTool(tb[0], tb[2], load_bitmap(tb[3]), shortHelp=tb[4], longHelp=tb[4])
            if tb[-1]:
                self.Bind(wx.EVT_TOOL, getattr(self, tb[-1]), id=tb[0])

        searchctl = search.MailSearchCtrl(self.toolbar, size=(180,-1), doSearch=self.DoSearch)
        self.toolbar.AddControl(searchctl)

        self.toolbar.Realize ()
        self.SetToolBar(self.toolbar)
       
    def create_menu_one(self, menu):
        m = PicMenu(self)
        for sub in menu:
            #print sub
            if type(sub) != type([]):
                m.AppendSeparator()
                continue
            setattr(self, sub[1], sub[0])
            #self.menus[uiconfig.menu[i]] = m
            if sub[5]:
                m2 = self.create_menu_one(sub[5])
                m.AppendMenu(sub[0], sub[2], m2)
            else:
                m.Append(sub[0], sub[2], sub[3])
            if sub[4]:
                self.Bind(wx.EVT_MENU, getattr(self, sub[4]), id=sub[0])
   
                
        return m
 
    def make_menu(self):        
        self.menus = {}
        menubar = wx.MenuBar()

        for i in range(0, len(uiconfig.menu), 2):
            submenus = uiconfig.menu[i+1]
            m = self.create_menu_one(submenus)
            self.menus[uiconfig.menu[i]] = m
            menubar.Append(m, uiconfig.menu[i])
                
        self.SetMenuBar(menubar)

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
        x = {'name':data['user'], 'task':'recvmail'}
        loginfo('add taskq: last_mailbox:', data['user'], 'task:', x)
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

    def OnEncodeAuto(self, event):
        pass

    def OnEncodeGBK(self, event):
        pass

    def OnEncodeGB18030(self, event):
        pass

    def OnEncodeBIG5(self, event):
        pass

    def OnEncodeUTF8(self, event):
        pass
       
    def OnImportOutlookUser(self, event):
        pass       
    def OnImportOutlookMailbox(self, event):
        pass
    def OnImportOutlookContact(self, event):
        pass
    def OnImportFoxmailUser(self, event):
        pass
    def OnImportFoxmailMailbox(self, event):
        pass
    def OnImportFoxmailContact(self, event):
        pass
    def OnImportCuteUser(self, event):
        pass
    def OnImportCuteMailbox(self, event):
        pass
    def OnImportCuteContact(self, event):
        pass
        
        
    def OnExportCuteUser(self, event):
        pass
    def OnExportCuteMailbox(self, event):
        pass
    def OnExportCuteContact(self, event):
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
            if me['name']:
                try:
                    conf = config.cf.user_add(me)
                except Exception, e:
                    wx.MessageBox(u"用户添加失败!"+str(e), u"欢迎使用CuteMail")
                else:
                    #wx.MessageBox(u"用户添加成功!", u"欢迎使用CuteMail")
                    self.tree.append(conf['mailbox'], me['name'])
                    self.tree.Refresh()
            else:
                dlg = wx.MessageDialog(self, u'用户名不能为空', u'错误', wx.OK)
                dlg.Destroy()
                    
        
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
    
    def OnMailSearch(self, event):
        pass

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
        info.Developers = ["zhaoweikid"]

        info.License = wordwrap("GPL", 500, wx.ClientDC(self))
        wx.AboutBox(info)

    def OnWebsite(self, event):
        self.display_mailbox(u'/')
        
        
        
