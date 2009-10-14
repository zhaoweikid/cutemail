# coding: utf-8
import os, sys, time, simplejson
import wx, wx.gizmos
import  wx.lib.dialogs
import cStringIO, types
import config, common, dbope, utils, mailparse
from optiondlg import OptionsDialog
from common import load_bitmap
import logfile, viewer
from logfile import loginfo, logwarn, logerr
        
class MailListPanel(wx.Panel):
    def __init__(self, parent, path):       
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.tree = wx.gizmos.TreeListCtrl(self, -1, style = wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT)
            
        self.path = path

        parts = path.split('/')
        self.user = parts[1]
        if len(parts) > 2:
            self.boxname = parts[2]
        else:
            self.boxname = ''
        loginfo('boxname:', self.boxname)
        self.il = wx.ImageList(16, 16)
        #self.idx = self.il.Add(images.getSmilesBitmap())
        
        self.tree.SetImageList(self.il)
        cols = [u'发件人','attach',u'邮件主题','mark',u'日期']
        
        self.lastitem = None

        self.image_attach = config.cf.home+'/bitmaps/16/attach.png'
        self.image_flag = config.cf.home+'/bitmaps/16/flag.png'
        self.image_mark = config.cf.home+'/bitmaps/16/bookmark.png'
        self.pngs = {self.image_attach:0, self.image_flag:0, self.image_mark:0}
        
        for k in self.pngs:
            #loginfo('load png:', k)
            try:
                self.pngs[k] = self.il.Add(load_bitmap(k))
            except:
                testfile = os.path.join(config.cf.home , 'bitmaps/16/blender.png')
                self.pngs[k] = self.il.Add(load_bitmap(testfile))
        
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
        
        self.earlier = self.add_item([u' 更早 ',0,'',0,'', wx.TreeItemData({'new':0, 'all':0})])
        self.month = self.add_item([u' 本月 ',0,'',0,'', wx.TreeItemData({'new':0, 'all':0})]) 
        self.week  = self.add_item([u' 本周 ',0,'',0,'', wx.TreeItemData({'new':0, 'all':0})]) 
        self.yestoday = self.add_item([u' 昨天 ',0,'',0,'', wx.TreeItemData({'new':0, 'all':0})]) 
        self.today = self.add_item([u' 今天 ',0,'',0,'', wx.TreeItemData({'new':0, 'all':0})]) 

        self.parent_items = [self.earlier, self.month, self.week, self.yestoday, self.today]
        
        timenow = time.localtime()
        self.time_today = time.mktime((timenow[0], timenow[1], timenow[2], 0, 0, 0, 0, 0, 0))
        self.time_yestoday = self.time_today - 86400
        self.time_week = self.time_today - 86400 * timenow[6]
        self.time_month = time.mktime((timenow[0], timenow[1], 1, 0, 0, 0, 0, 0, 0))
        
        self.mail_new = 0
        self.mail_all = 0
        #self.add_item(item, self.week)
        #self.add_item(item, self.yestoday)
        #self.add_item(item, self.today)
        
        self.tree.Expand(self.root)
        self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        #self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
        self.tree.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnActivate)
        self.tree.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)

    def draw_category_text(self, item, action='add'):
        '''action: add/del/read/display'''
        parent = self.tree.GetItemParent(item)
        itemdata = self.tree.GetItemData(item).GetData()
        text = self.tree.GetItemText(parent, 0)
        #loginfo('parent text:', text)
        data = self.tree.GetItemData(parent).GetData()
        #loginfo('parent data:', data)
        if action == 'add':
            data['all'] += 1
            self.mail_all += 1
        elif action == 'del':
            data['all'] -= 1
            self.mail_all -= 1

        if itemdata['status'] == 'noread':
            if action == 'add':
                data['new'] += 1
                self.mail_new += 1
            elif action == 'del':
                data['new'] -= 1
                self.mail_new -= 1
            elif action == 'read':
                data['new'] -= 1
                self.mail_new -= 1
                itemdata['status'] = 'read'
                #self.tree.SetItemBold(item, False) 
        #loginfo('draw category:', data)
        s = text.split(' ')    
        s[-1] = '%d/%d' % (data['new'], data['all'])
        self.tree.SetItemText(parent, ' '.join(s), 0)
        
        #if self.boxname == u'收件箱': 
        #    self.parent.tree.display_info(self.user, u'收件箱', self.mail_new, self.mail_all)
        self.parent.tree.display_info(self.user, self.boxname, self.mail_new, self.mail_all)


    def draw_mail_status_read(self, item):
        self.tree.SetItemBold(item, False) 

    def select_all_items(self):
        items = []
        for item in self.parent_items:
            ret = self.get_all_children(item)
            if ret:
                items.extend(ret)
        #loginfo('select items:', items)
        if items:
            for item in items:
                #loginfo('try select:', item)
                self.tree.ToggleItemSelection(item)

    def get_all_children(self, parent):
        ret = []
        child,cookie = self.tree.GetFirstChild(parent)
        if not child:
            return ret
        ret.append(child)
        while True:
            other, cookie = self.tree.GetNextChild(parent, cookie)
            if not other:
                return ret
            ret.append(other)

    
    def add_item(self, item, parent=None):
        #loginfo('add item:', item)
        if not parent:
            parent = self.root

        first = self.tree.PrependItem(parent, '')
        self.tree.SetItemText(first, item[0], 0)
        if item[1]:
            self.tree.SetItemImage(first, self.pngs[self.image_attach], 1)
        #if item[2]:
        #    self.tree.SetItemImage(first, self.pngs[self.image_flag], 2)
        self.tree.SetItemText(first, item[2], 2)
        if item[3]:
            self.tree.SetItemImage(first, self.pngs[self.image_mark], 3)
        self.tree.SetItemText(first, item[4][:-3], 4)
        #self.tree.SetItemText(first, item[5], 5)
        self.tree.SetItemData(first, item[5]) 
       
        if parent != self.root:
            self.draw_category_text(first, 'add')
            itemdata = item[5].GetData()
            if itemdata['status'] == 'noread':
                self.tree.SetItemBold(first, True)

        return first
       
    def add_mail(self, item):
        if item[4] and item[4] != 'None':
            timels = time.strptime(item[4], '%Y-%m-%d %H:%M:%S')
        else:
            timels = time.localtime()
        mtime = time.mktime(timels)
        #print 'make time:', mtime
        if mtime >= self.time_today:
            return self.add_item(item, self.today)
        elif mtime >= self.time_yestoday:
            return self.add_item(item, self.yestoday)
        elif mtime >= self.time_week:
            return self.add_item(item, self.week)
        elif mtime >= self.time_month:
            return self.add_item(item, self.month)
        else:
            return self.add_item(item, self.earlier)
    
    def remove_item(self, item=None):
        if not item:
            item = self.lastitem
        if not item:
            raise ValueError, 'item must not None'
    
        self.draw_category_text(item, 'del')
        self.tree.Delete(item) 
        
    def make_popup_menu(self):
        if not hasattr(self, 'ID_POPUP_REPLY'):
            self.ID_POPUP_REPLY = wx.NewId()
            self.ID_POPUP_FORWARD = wx.NewId()
            self.ID_POPUP_SEND_SEC = wx.NewId()
            self.ID_POPUP_CONTACT_ADD = wx.NewId()
            self.ID_POPUP_VIEW = wx.NewId()
            self.ID_POPUP_SOURCE = wx.NewId()
            self.ID_POPUP_DELETE = wx.NewId()
            
            self.Bind(wx.EVT_MENU, self.OnPopupReply, id=self.ID_POPUP_REPLY) 
            self.Bind(wx.EVT_MENU, self.OnPopupForward, id=self.ID_POPUP_FORWARD) 
            self.Bind(wx.EVT_MENU, self.OnPopupSendSec, id=self.ID_POPUP_SEND_SEC) 
            self.Bind(wx.EVT_MENU, self.OnPopupContactAdd, id=self.ID_POPUP_CONTACT_ADD) 
            self.Bind(wx.EVT_MENU, self.OnPopupView, id=self.ID_POPUP_VIEW) 
            self.Bind(wx.EVT_MENU, self.OnPopupSource, id=self.ID_POPUP_SOURCE) 
            self.Bind(wx.EVT_MENU, self.OnPopupDelete, id=self.ID_POPUP_DELETE) 
            
        menu = wx.Menu()
        menu.Append(self.ID_POPUP_REPLY, u'回复邮件')
        menu.Append(self.ID_POPUP_FORWARD, u'转发邮件')
        menu.Append(self.ID_POPUP_SEND_SEC, u'再次发送邮件')
        menu.AppendSeparator()
        menu.Append(self.ID_POPUP_CONTACT_ADD, u'添加发件人为联系人')
        menu.AppendSeparator()
        menu.Append(self.ID_POPUP_VIEW, u'查看邮件')
        menu.AppendSeparator()
        menu.Append(self.ID_POPUP_DELETE, u'删除邮件')
        menu.AppendSeparator()
        menu.Append(self.ID_POPUP_SOURCE, u'信件原文')
        
        self.PopupMenu(menu)
        menu.Destroy()

    def get_item_data(self, item=None):
        if not item:
            item = self.lastitem
        if not item:
            raise ValueError, 'item must not None'
        
        data = self.tree.GetItemData(item).GetData()
        return data 

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

    def change_box(self, info, newbox='trash'):
        id = info['id']
        mailbox = info['mailbox'] 
        if newbox == 'recv':
            basepath = os.path.basename(info['filename'])
            datestr = info['ctime'][:6]
            hashstr = '%02d' % (hash(basepath) % 10)
            newfilename = os.path.join(datestr, hashstr, basepath)
        else:
            newfilename = os.path.basename(info['filename'])

        loginfo('change box from:', mailbox, ' to:', newbox)
        if mailbox == 'trash': 
            sql = "delete from mailinfo where id=%s" % (str(id))
        else:
            sql = "update mailinfo set mailbox='%s',filename='%s' where id=%s" % (newbox, newfilename, str(id))
        loginfo('delete:', sql)
        
        username = info['user']
        db = dbope.openuser(config.cf, username)
        db.execute(sql)
        db.close()
        
        if info.has_key('item'):
            loginfo('info item:', info['item'])
            item = info['item']
        else:
            loginfo('not found item in info')
            item = self.lastitem
        loginfo('item: ', item)
        self.remove_item(item)
        self.parent.load_db_one(username, id)
        
        if mailbox == 'trash':
            os.remove(info['filepath']) 
        else:
            newfile = os.path.join(config.cf.datadir, username, newbox, newfilename)
            loginfo('newfile:', newfile)
            os.rename(info['filepath'], newfile)

    def change_last_box(self, newbox='trash'):
        try:
            info = self.get_item_data()
        except Exception, e:
            logerr('get_item_content error:', str(e))
            return
         
        self.change_box(info, newbox)

    def OnPopupReply(self, evt):
        self.parent.OnMailReply(evt)

    def OnPopupForward(self, evt):
        self.parent.OnMailForward(evt)
    
    def OnPopupSendSec(self, evt):
        self.parent.OnMailSendSec(evt)

    def OnPopupContactAdd(self, evt):
        if self.lastitem:
            s = self.tree.GetItemData(self.lastitem).GetData()
            if not s:
                return
            loginfo('Source:', s)
            mfrom = s['mailfrom'] 
            item = config.cf.linkman.add(mfrom, mfrom)
            ctree = self.parent.contact
            ctree.add(item)

    def OnPopupView(self, evt):
        if self.lastitem:
            s = self.tree.GetItemData(self.lastitem).GetData()
            if not s:
                return
        filepath = s['filepath']
        frame = viewer.MailViewFrame(self, self.parent.rundir, s['user'], filepath)
        frame.Show()

    def OnPopupSource(self, evt):
        if self.lastitem:
            s = self.tree.GetItemData(self.lastitem).GetData()
            if not s:
                return
            loginfo('Source:', s)
            filepath = os.path.join(config.cf.datadir, s['user'], s['mailbox'], s['filename'].lstrip(os.sep))
            loginfo('filepath:', filepath)
            f = open(filepath, 'r')
            source = f.read()
            f.close()
            
            # fix me: use gbk and utf-8 is not a good idear
            try:
                source = unicode(source, 'gbk')
            except:
                source = unicode(source, 'utf-8')


            dlg = wx.lib.dialogs.ScrolledMessageDialog(self, source, u'信件原文',
                                size = (800, 600), 
                                style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
            dlg.ShowModal()
       
    def OnPopupDelete(self, evt):
        loginfo('delete mail')
        self.change_last_box('trash')

    def OnActivate(self, evt):
        #loginfo('event:', evt)
        loginfo('OnActivate: %s' % self.tree.GetItemText(evt.GetItem()))
        self.lastitem = evt.GetItem()
        row = self.tree.GetItemData(evt.GetItem()).GetData()
        #loginfo('active row:', row)
        if not row:
            logerr('not found row.')
            return
        if not row.has_key('id'):
            loginfo('is category.')
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
        
        #row['attach'] = simplejson.loads(row['attach'])

        for item in row['attach']:
            filename = os.path.join(config.cf.datadir, name, row['mailbox'], row['filename'].strip(os.sep))
            homename = os.path.join(config.cf.datadir, name)
            attachdata = {'file':filename, 'home':homename, 'attach':item[0]}
            loginfo('attachdata:', attachdata)
            attachctl.add_file(item[0], attachdata)

        if row['status'] == 'noread':
            #row['status'] = 'read' 
            item = evt.GetItem()
            itemdata = self.tree.GetItemData(item).GetData()
            #loginfo('noread itemdata:', itemdata)
            self.draw_category_text(item, 'read')
            self.tree.SetItemBold(item, False)
        
            sql = "update mailinfo set status='read' where id=" + str(itemdata['id'])
            loginfo('read:', sql)
            db = dbope.openuser(config.cf, name)
            db.execute(sql)
            db.close()

    def OnRightUp(self, evt):
        pos = evt.GetPosition()
        self.tree.HitTest(pos)
        item, flags, col = self.tree.HitTest(pos)
        if item:
            self.tree.SelectItem(item)
            #print 'Flags: %s, Col:%s, Text: %s' % (flags, col, self.tree.GetItemText(item, col))
            
        self.make_popup_menu()

    def OnLeftDClick(self, evt):
        loginfo('left double click')
        if self.lastitem:
            s = self.tree.GetItemData(self.lastitem).GetData()
            if not s:
                return
        filepath = s['filepath']
        frame = viewer.MailViewFrame(self, self.parent.rundir, s['user'], filepath)
        frame.Show()
    
    def OnSize(self, evt):
        self.tree.SetSize(self.GetSize())

    def OnColClick(self, evt):
        loginfo('col click')

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
        
        self.usertree = {}
        self.load()
       
    def display_info(self, user, boxname, newnum, allnum):
        child = self.GetFirstChild(self.root)
        curitem = child[0]
        #loginfo('curitem:', curitem)
        while True:
            text = self.GetItemText(curitem)
            #loginfo('sibling text:', text)
            if text.startswith(boxname):
                break
            curitem = self.GetNextSibling(curitem)
            if not curitem:
                break
        s = '%s %d/%d' % (boxname, newnum, allnum)
        self.SetItemText(self.usertree[user][boxname], s)

    def last_item(self):
        return self.GetSelection()
    
    def last_item_data(self):
        item = self.GetSelection()
        return self.GetPyData(item)
    
    def last_item_remove(self):
        data = self.last_item_data()
        loginfo('data:', data)
        dlg = wx.MessageDialog(self, u'删除该邮件夹的同时会删除里面的所有邮件!', u'注意',
                               wx.YES_NO|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.NO:
            dlg.Destroy()
            loginfo('return, not remove')
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
        
        loginfo('newpath:', newpath)
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
            self.usertree[k] = {}
            self.add_to_tree(self.root, mbox, k, [])
        
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self) 
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

    def add_tree_node(self, parent, name, user, tpath):
        item  = self.AppendItem(parent, name)
        loginfo('add mail panel:', tpath)
        panel = self.parent.add_mailbox_panel(tpath)
        
        data = {'path':tpath, 'user':user, 'boxname':name, 'item':item, 'panel':panel}
        #loginfo('tree node data:', data)
        self.SetPyData(item, data)
        self.SetItemImage(item, self.ridx, wx.TreeItemIcon_Normal)
        self.SetItemImage(item, self.openidx, wx.TreeItemIcon_Expanded)

        return item
            
    def add_to_tree(self, parent, name, user, tpathls):
        loginfo('add_to_tree:', name)
        loginfo('tpathls:', tpathls)
        if tpathls:
            tpath = '/' + '/'.join(tpathls) + '/' + name[0]
        else:
            tpath = '/' + name[0]

        loginfo('tpath:', tpath)
        
        p = self.add_tree_node(parent, name[0], user, tpath)
        if len(tpathls) == 1:
            if not self.usertree.has_key(tpathls[0]):
                self.usertree[tpathls[0]] = {}
            self.usertree[tpathls[0]][name[0]] = p
        tpathls.append(name[0])
        for child in name[1]:
            self.add_to_tree(p, child, user, tpathls)
            tpathls.pop(-1)
            
        
    def append(self, name, user, tpathls=None):
        if not tpathls:
            tpathls = []
        self.add_to_tree(self.root, name, user, tpathls) 
    
    
    def make_popup_menu(self):
        if not hasattr(self, 'ID_POPUP_RECV'):
            self.ID_POPUP_RECV = wx.NewId()
            self.ID_POPUP_SEND = wx.NewId()
            self.ID_POPUP_MAILBOX_NEW = wx.NewId()
            self.ID_POPUP_MAILBOX_RENAME = wx.NewId()
            self.ID_POPUP_SETTING = wx.NewId()
            
            self.Bind(wx.EVT_MENU, self.OnPopupRecv, id=self.ID_POPUP_RECV)
            self.Bind(wx.EVT_MENU, self.OnPopupSend, id=self.ID_POPUP_SEND)
            self.Bind(wx.EVT_MENU, self.OnPopupMailboxNew, id=self.ID_POPUP_MAILBOX_NEW)
            self.Bind(wx.EVT_MENU, self.OnPopupMailboxRename, id=self.ID_POPUP_MAILBOX_RENAME)
            self.Bind(wx.EVT_MENU, self.OnPopupSetting, id=self.ID_POPUP_SETTING)
            
        menu = wx.Menu()
        menu.Append(self.ID_POPUP_RECV, u'收取邮件')
        menu.Append(self.ID_POPUP_SEND, u'发送发件箱内邮件')
        menu.AppendSeparator()
        menu.Append(self.ID_POPUP_MAILBOX_NEW, u'新建邮件夹')
        menu.Append(self.ID_POPUP_MAILBOX_RENAME, u'重命名邮件夹')
        menu.AppendSeparator()
        menu.Append(self.ID_POPUP_SETTING, u'属性设置')
        self.PopupMenu(menu)
        menu.Destroy()
    
    def OnPopupRecv(self, evt):
        self.parent.OnFileGetMail(evt)
    
    def OnPopupSend(self, evt):
        self.parent.OnFileSendMail(evt)
    
    def OnPopupMailboxNew(self, evt):
        self.parent.OnMailboxNew(evt)
    
    def OnPopupMailboxRename(self, evt):
        self.parent.OnMailboxRename(evt)
        
    def OnPopupSetting(self, evt):
        self.popup_setting()
        
    def popup_setting(self):
        data = self.last_item_data()
        usercf = config.cf.users[data['user']]
        dlg = OptionsDialog(self, usercf)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.get_values()
            for k in data:
                usercf[k] = data[k]
            config.cf.dump_conf(usercf)

    def OnSelChanged(self, evt):
        self.item = evt.GetItem()
        if self.item:
            data = self.GetPyData(self.item)
            #loginfo(data)
            
            tpath = data['path']
            loginfo('OnSelChanged path:', tpath)
            
            self.parent.display_mailbox(tpath)
            
            
    def OnSize(self, evt):
        self.SetSize(self.GetSize())

    def OnRightUp(self, evt):
        loginfo('tree right up...')
        pt = evt.GetPosition()
        item, flags = self.HitTest(pt)
        
        self.make_popup_menu()
        
        
    
        
        
