# coding: utf-8
import os, sys, time
import wx, wx.gizmos
import  wx.lib.dialogs
import cStringIO, types
import config, common, dbope, utils, mailparse
        
class MailListPanel(wx.Panel):
    def __init__(self, parent, flag=''):       
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.tree = wx.gizmos.TreeListCtrl(self, -1, style = wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT)
        
        self.il = wx.ImageList(16, 16)
        #self.idx = self.il.Add(images.getSmilesBitmap())
        
        self.tree.SetImageList(self.il)
        if flag:
            cols = [u'发件人','attach','mark',u'邮件主题',u'日期',u'邮件大小']
        else:
            cols = [u'发件人','attach','mark',u'邮件主题',u'日期',u'邮件大小']
        
        item = ['zhaowei@bobo.com', 1,1, u'呵呵我的测试', '20090210', '12873']
        self.lastitem = None

        self.image_attach = config.cf.home+'/bitmaps/16/attach.png'
        self.image_flag = config.cf.home+'/bitmaps/16/flag.png'
        self.image_mark = config.cf.home+'/bitmaps/16/bookmark.png'
        self.pngs = {self.image_attach:0, self.image_flag:0, self.image_mark:0}
        
        for k in self.pngs:
            self.pngs[k] = self.il.Add(common.load_bitmap(k))
        
        for c in cols:        
            if c == 'attach':
                info = wx.gizmos.TreeListColumnInfo()
                info.SetImage(self.pngs[self.image_attach])                
                info.SetWidth(22)
                self.tree.AddColumnInfo(info)
            elif c == 'flag':
                info = wx.gizmos.TreeListColumnInfo()
                info.SetImage(self.pngs[self.image_flag])                
                info.SetWidth(22)
                self.tree.AddColumnInfo(info)
            elif c == 'mark':
                info = wx.gizmos.TreeListColumnInfo()
                info.SetImage(self.pngs[self.image_mark])                
                info.SetWidth(22)
                self.tree.AddColumnInfo(info)
            elif c == u'发件人':                
                info = wx.gizmos.TreeListColumnInfo()
                info.SetText(c)                
                info.SetWidth(200)
                self.tree.AddColumnInfo(info)
            elif c == u'邮件主题':
                info = wx.gizmos.TreeListColumnInfo()
                info.SetText(c)                
                info.SetWidth(300)
                self.tree.AddColumnInfo(info)
            elif c == u'日期':
                info = wx.gizmos.TreeListColumnInfo()
                info.SetText(c)                
                info.SetWidth(130)
                self.tree.AddColumnInfo(info)
            else:
                self.tree.AddColumn(c)
        self.tree.SetMainColumn(0)
        self.root = self.tree.AddRoot("root")
        
        self.earlier = self.add_item([u' 更早 ',0,0,'','','', wx.TreeItemData(None)])
        self.month = self.add_item([u' 本月 ',0,0,'','','', wx.TreeItemData(None)]) 
        self.week  = self.add_item([u' 本周 ',0,0,'','','', wx.TreeItemData(None)]) 
        self.yestoday = self.add_item([u' 昨天 ',0,0,'','','', wx.TreeItemData(None)]) 
        self.today = self.add_item([u' 今天 ',0,0,'','','', wx.TreeItemData(None)]) 
        
        timenow = time.localtime()
        self.time_today = time.mktime((timenow[0], timenow[1], timenow[2], 0, 0, 0, 0, 0, 0))
        self.time_yestoday = self.time_today - 86400
        self.time_week = self.time_today - 86400 * timenow[6]
        self.time_month = time.mktime((timenow[0], timenow[1], 1, 0, 0, 0, 0, 0, 0))
        
        #self.add_item(item, self.week)
        #self.add_item(item, self.yestoday)
        #self.add_item(item, self.today)
        
        self.tree.Expand(self.root)
        self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        #self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnActivate)
        self.tree.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)

    def add_item(self, item, parent=None):
        if not parent:
            parent = self.root
        first = self.tree.PrependItem(parent, '')
        self.tree.SetItemText(first, item[0], 0)
        if item[1]:
            self.tree.SetItemImage(first, self.pngs[self.image_attach], 1)
        #if item[2]:
        #    self.tree.SetItemImage(first, self.pngs[self.image_flag], 2)
        if item[2]:
            self.tree.SetItemImage(first, self.pngs[self.image_mark], 2)
        self.tree.SetItemText(first, item[3], 3)
        self.tree.SetItemText(first, item[4], 4)
        self.tree.SetItemText(first, item[5], 5)
        self.tree.SetItemData(first, item[6]) 
            
        return first
       
    def add_mail(self, item):
        if item[4] and item[4] != 'None':
            timels = time.strptime(item[4], '%Y-%m-%d %H:%M:%S')
        else:
            timels = time.localtime()
        mtime = time.mktime(timels)
        #print 'make time:', mtime
        if mtime >= self.time_today:
            self.add_item(item, self.today)
        elif mtime >= self.time_yestoday:
            self.add_item(item, self.yestoday)
        elif mtime >= self.time_week:
            self.add_item(item, self.week)
        elif mtime >= self.time_month:
            self.add_item(item, self.month)
        else:
            self.add_item(item, self.earlier)
    
    def remove_item(self, item=None):
        if not item:
            item = self.lastitem
        if not item:
            raise ValueError, 'item must not None'
        self.tree.Delete(item) 
        
    def make_popup_menu(self):
        if not hasattr(self, 'ID_POPUP_REPLY'):
            self.ID_POPUP_REPLY = wx.NewId()
            self.ID_POPUP_FORWARD = wx.NewId()
            self.ID_POPUP_SEND_SEC = wx.NewId()
            self.ID_POPUP_VIEW = wx.NewId()
            self.ID_POPUP_SOURCE = wx.NewId()
            
            self.Bind(wx.EVT_MENU, self.OnPopupReply, id=self.ID_POPUP_REPLY) 
            self.Bind(wx.EVT_MENU, self.OnPopupForward, id=self.ID_POPUP_FORWARD) 
            self.Bind(wx.EVT_MENU, self.OnPopupSendSec, id=self.ID_POPUP_SEND_SEC) 
            self.Bind(wx.EVT_MENU, self.OnPopupView, id=self.ID_POPUP_VIEW) 
            self.Bind(wx.EVT_MENU, self.OnPopupSource, id=self.ID_POPUP_SOURCE) 
            
        menu = wx.Menu()
        menu.Append(self.ID_POPUP_REPLY, u'回复邮件')
        menu.Append(self.ID_POPUP_FORWARD, u'转发邮件')
        menu.Append(self.ID_POPUP_SEND_SEC, u'再次发送邮件')
        menu.AppendSeparator()
        menu.Append(self.ID_POPUP_VIEW, u'查看邮件')
        menu.AppendSeparator()
        menu.Append(self.ID_POPUP_SOURCE, u'信件原文')
        
        self.PopupMenu(menu)
        menu.Destroy()

    def get_item_content(self, item=None):
        if not item:
            item = self.lastitem
        if not item:
            raise ValueError, 'item must not None'
        
        data = self.tree.GetItemData(item).GetData()
        if not data:
            raise ValueError, "not found item data"
        
        info = mailparse.decode_mail(data['filepath'])
        data['html'] = info['html']
        data['plain'] = info['plain']
        
        return data

    def OnPopupReply(self, evt):
        pass
    
    def OnPopupForward(self, evt):
        pass
    def OnPopupSendSec(self, evt):
        pass
    def OnPopupView(self, evt):
        pass
    def OnPopupSource(self, evt):
        if self.lastitem:
            s = self.tree.GetItemData(self.lastitem).GetData()
            if not s:
                return
            print 'Source:', s
            filepath = os.path.join(config.cf.datadir, s['user'], s['mailbox'], s['filename'].lstrip(os.sep))
            print 'filepath:', filepath
            f = open(filepath, 'r')
            source = f.read()
            f.close()
            dlg = wx.lib.dialogs.ScrolledMessageDialog(self, source, u'信件原文',
                                size = (800, 600), 
                                style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
            dlg.ShowModal()
        
    def OnActivate(self, evt):
        print 'OnActivate: %s' % self.tree.GetItemText(evt.GetItem())
        self.lastitem = evt.GetItem()
        row = self.tree.GetItemData(evt.GetItem()).GetData()
        if not row:
            return
        #mid, name, mbox = s
        mid  = row['id']
        name = row['user']
        mbox = row['box']
        
        info = mailparse.decode_mail(row['filepath'])
        
        htmldata = info['html']
        plaindata = info['plain']
        if htmldata:
            self.parent.listcnt.set_text(htmldata)
        elif plaindata:
            self.parent.listcnt.set_text(plaindata.replace('\r\n', '<br>').replace('\n', '<br>'))
        attachctl = self.parent.attachctl
        attachctl.clear()
        if row['attach']:
            attach = row['attach'].split('||')
            if attach:
                pos = 0
                for a in attach:
                    item = a.split('::')
                    filename = os.path.join(config.cf.datadir, name, row['mailbox'], row['filename'].strip(os.sep))
                    homename = os.path.join(config.cf.datadir, name)
                    attachdata = {'file':filename, 'home':homename, 'attach':item[0]}
                    print 'attachdata:', attachdata
                    attachctl.add_file(item[0], attachdata)
                    pos += 1

    def OnRightUp(self, evt):
        pos = evt.GetPosition()
        self.tree.HitTest(pos)
        item, flags, col = self.tree.HitTest(pos)
        if item:
            self.tree.SelectItem(item)
            print 'Flags: %s, Col:%s, Text: %s' % (flags, col, self.tree.GetItemText(item, col))
            
        self.make_popup_menu()

    def OnSize(self, evt):
        self.tree.SetSize(self.GetSize())

    def OnColClick(self, evt):
        print 'col click'

class MailboxTree(wx.TreeCtrl):
    def __init__(self, parent):
        self.parent = parent
        super(MailboxTree, self).__init__(parent, wx.NewId(), wx.Point(0, 0), wx.Size(200, 200), 
                    style = wx.TR_DEFAULT_STYLE |wx.TR_HIDE_ROOT)
                    #style = wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT)
        isz = (16,16)       
        il = wx.ImageList(isz[0], isz[1])
        rootidx  = il.Add(wx.BitmapFromImage(wx.ImageFromStream(cStringIO.StringIO(open('bitmaps/16/user.png','rb').read()))))
        self.ridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        self.openidx  = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        self.fidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_REPORT_VIEW, wx.ART_OTHER, isz))   
        self.SetImageList(il)
        self.il = il
        
        self.load()
        
    def last_item(self):
        return self.GetSelection()
    
    def last_item_data(self):
        item = self.GetSelection()
        return self.GetPyData(item)
    
    def last_item_remove(self):
        data = self.last_item_data()
        print 'data:', data
        dlg = wx.MessageDialog(self, u'删除该邮件夹的同时会删除里面的所有邮件!', u'注意',
                               wx.YES_NO|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.NO:
            dlg.Destroy()
            print 'return, not remove'
            return
        dlg.Destroy() 
        usercf = config.cf.users[data['user']]
        mailbox = usercf['mailbox'] 
        parts = data['path'].split('/')
        del parts[0]
            
        utils.mailbox_remove(mailbox, parts)
        config.cf.dump_conf(data['user'])
        #panel = self.parent.mailboxs[data['path']]
        #panel.Destroy()
        #del self.parent.mailboxs[data['path']]
        self.Delete(data['item'])
        
        # 把数据库中这个邮件夹的邮件全部移动到已删除
    
    def last_item_rename(self):
        data = self.last_item_data()
        
        dlg = wx.TextEntryDialog(self, u'邮件夹' + data['boxname'] + u'重命名为:')
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()
        else:
            dlg.Destroy()
            return
        dlg.Destroy()
        
        usercf = config.cf.users[data['user']]
        mailbox = usercf['mailbox'] 
        parts = data['path'].split('/')
        del parts[0]
        item = data['item']
        utils.mailbox_rename(mailbox, parts, name)
        
        parts[-1] = name
        config.cf.dump_conf(data['user'])
        newpath = '/' + '/'.join(parts)
        
        print 'newpath:', newpath
        oldpanel = self.parent.mailboxs[data['path']]
        del self.parent.mailboxs[data['path']]
        self.parent.mailboxs[newpath] = oldpanel
        self.parent.mgr.AddPane(oldpanel, wx.aui.AuiPaneInfo().Name(newpath).CenterPane().Hide())
        
        data['path'] = newpath
        data['boxname'] = name
        
        self.SetItemText(item, name)
        # 数据库中所有这个邮件夹的邮件要改mailbox字段
        
    def last_item_add_child(self):
        data = self.last_item_data()
        
        dlg = wx.TextEntryDialog(self, u'新邮件夹名字:')
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()
        else:
            dlg.Destroy()
            return
        dlg.Destroy()
        
        usercf = config.cf.users[data['user']]
        mailbox = usercf['mailbox'] 
        parts = data['path'].split('/')
        del parts[0]
        item = data['item']
        
        utils.mailbox_add(mailbox, parts, name)
        
        parts.append(name)
        newpath = '/' + '/'.join(parts)        
        child = self.add_tree_node(item, name, data['user'], newpath)
        self.SetItemText(child, name)
        
        config.cf.dump_conf(data['user'])
        
    def load(self):
        self.root = self.AddRoot("/")
        
        for k in config.cf.users:
            usercf = config.cf.users[k]
            #print 'user:', k, usercf
            mbox = usercf['mailbox']
            #tpathls = [] 
            self.add_to_tree(self.root, mbox, k)
        
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self) 
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

    def add_tree_node(self, parent, name, user, tpath):
        item  = self.AppendItem(parent, name)
        panel = self.parent.add_mailbox_panel(tpath)
        
        data = {'path':tpath, 'user':user, 'boxname':name, 'item':item, 'panel':panel}
        self.SetPyData(item, data)
        self.SetItemImage(item, self.ridx, wx.TreeItemIcon_Normal)
        self.SetItemImage(item, self.openidx, wx.TreeItemIcon_Expanded)

        return item
            
    def add_to_tree(self, parent, name, user, tpathls=[]):
        print 'add_to_tree:', name
        tpath = '/' + '/'.join(tpathls) + '/' + name[0]
        print 'tpath:', tpath
        
        p = self.add_tree_node(parent, name[0], user, tpath)
        tpathls.append(name[0])
        for child in name[1]:
            self.add_to_tree(p, child, user, tpathls)
            tpathls.pop(-1)
            
        
    def append(self, name, user, tpathls=[]):
        self.add_to_tree(self.root, name, user, tpathls) 
    
    
    def make_popup_menu(self):
        if not hasattr(self, 'ID_POPUP_RECV'):
            self.ID_POPUP_RECV = wx.NewId()
            self.ID_POPUP_SEND = wx.NewId()
            self.ID_POPUP_MAILBOX_NEW = wx.NewId()
            self.ID_POPUP_MAILBOX_RENAME = wx.NewId()
            self.ID_POPUP_PASSWORD = wx.NewId()
            self.ID_POPUP_FILTER = wx.NewId()
            self.ID_POPUP_SETTING = wx.NewId()
            
            self.Bind(wx.EVT_MENU, self.OnPopupRecv, id=self.ID_POPUP_RECV)
            self.Bind(wx.EVT_MENU, self.OnPopupSend, id=self.ID_POPUP_SEND)
            self.Bind(wx.EVT_MENU, self.OnPopupMailboxNew, id=self.ID_POPUP_MAILBOX_NEW)
            self.Bind(wx.EVT_MENU, self.OnPopupMailboxRename, id=self.ID_POPUP_MAILBOX_RENAME)
            self.Bind(wx.EVT_MENU, self.OnPopupPassword, id=self.ID_POPUP_PASSWORD)
            self.Bind(wx.EVT_MENU, self.OnPopupFilter, id=self.ID_POPUP_FILTER)
            self.Bind(wx.EVT_MENU, self.OnPopupSetting, id=self.ID_POPUP_SETTING)
            
        menu = wx.Menu()
        menu.Append(self.ID_POPUP_RECV, u'收取邮件')
        menu.Append(self.ID_POPUP_SEND, u'发送发件箱内邮件')
        menu.AppendSeparator()
        menu.Append(self.ID_POPUP_MAILBOX_NEW, u'新建邮箱')
        menu.Append(self.ID_POPUP_MAILBOX_RENAME, u'重命名邮箱')
        menu.AppendSeparator()
        menu.Append(self.ID_POPUP_PASSWORD, u'设置密码')
        menu.Append(self.ID_POPUP_FILTER, u'设置过滤器')
        menu.AppendSeparator()
        menu.Append(self.ID_POPUP_SETTING, u'属性设置')
        self.PopupMenu(menu)
        menu.Destroy()
    
    def OnPopupRecv(self, evt):
        pass
    
    def OnPopupSend(self, evt):
        pass
    
    def OnPopupMailboxNew(self, evt):
        pass
    def OnPopupMailboxRename(self, evt):
        pass
    def OnPopupPassword(self, evt):
        pass
    def OnPopupFilter(self, evt):
        pass
    
    def OnPopupSetting(self, evt):
        pass
    def OnSelChanged(self, evt):
        self.item = evt.GetItem()
        if self.item:
            data = self.GetPyData(self.item)
            print data
            
            tpath = data['path']
            print 'OnSelChanged path:', tpath
            
            self.parent.display_mailbox(tpath)
            
            
    def OnSize(self, evt):
        self.SetSize(self.GetSize())

    def OnRightUp(self, evt):
        print 'tree right up...'
        pt = evt.GetPosition()
        item, flags = self.HitTest(pt)
        
        self.make_popup_menu()
        
        
    
        
        
