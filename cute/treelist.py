# coding: utf-8
import os, sys, time
import wx, wx.gizmos
import cStringIO, types
import config, common, dbope
        
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


        self.image_attach = config.cf.home+'/bitmaps/16/attach.png'
        self.image_flag = config.cf.home+'/bitmaps/16/flag.png'
        self.image_mark = config.cf.home+'/bitmaps/16/bookmark.png'
        self.pngs = {self.image_attach:0, self.image_flag:0, self.image_mark:0}
        
        for k in self.pngs:
            self.pngs[k] = self.il.Add(common.load_image(k))
        
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
        print 'add_mail:', item
        if item[4] and item[4] != 'None':
            timels = time.strptime(item[4], '%Y-%m-%d %H:%M:%S')
        else:
            timels = time.localtime()
        print 'timels:', timels
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

    def OnActivate(self, evt):
        print 'OnActivate: %s' % self.tree.GetItemText(evt.GetItem())
        s = self.tree.GetItemData(evt.GetItem()).GetData()
        if not s:
            return
        mid, name, mlist = s
        sql = "select * from mailinfo where id=" + mid
        
        dbpath = os.path.join(config.cf.datadir, name, 'mailinfo.db')
        print 'dbpath:', dbpath
        conn = dbope.DBOpe(dbpath)
        ret = conn.query(sql)
        conn.close()
        if ret:
            row = ret[0]
            htmldata = row['html']
            plaindata = row['plain']
            if htmldata:
                self.parent.listcnt.set_text(htmldata)
            elif plaindata:
                self.parent.listcnt.set_text(plaindata.replace('\r\n', '<br>').replace('\n', '<br>'))
            attachctl = self.parent.attachctl
            attachctl.ClearAll()
            if row['attach']:
                attach = row['attach'].split('||')
                if attach:
                    pos = 0
                    for a in attach:
                        item = a.split('::')
                        attachctl.InsertImageStringItem(pos, item[0], attachctl.image_default)
                        filename = os.path.join(config.cf.datadir, name, row['mailbox'], row['filename'])
                        homename = os.path.join(config.cf.datadir, name)
                        attachctl.SetItemData(pos, {'file':filename, 'home':homename, 'attach':item[0]})
                        pos += 1

    def OnRightUp(self, evt):
        pos = evt.GetPosition()
        item, flags, col = self.tree.HitTest(pos)
        if item:
            print 'Flags: %s, Col:%s, Text: %s' % (flags, col, self.tree.GetItemText(item, col))

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
        
    def load(self):
        self.root = self.AddRoot("/")
        
        for k in config.cf.users:
            usercf = config.cf.users[k]
            print 'user:', k, usercf
            mbox = usercf['mailbox']
            #tpathls = [] 
            self.add_to_tree(self.root, mbox)
        
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self) 

    def add_to_tree(self, parent, name, tpathls=[]):
        if type(name) == types.ListType:
            p = self.add_to_tree(parent, name[0], tpathls)
            tpathls.append(name[0])
            for x in name[1:]:
                self.add_to_tree(p, x, tpathls)
            tpathls.remove(name[0])
            return p
        item = self.AppendItem(parent, name)
        self.SetPyData(item, None)
        self.SetItemImage(item, self.ridx, wx.TreeItemIcon_Normal)
        self.SetItemImage(item, self.openidx, wx.TreeItemIcon_Expanded)
        #self.EnsureVisible(item)
        
        tpath = '/'.join(tpathls) + '/' + name
        if tpath[0] != '/':
            tpath = '/' + tpath
        print 'tpath:', tpath
        self.parent.add_mailbox_panel(tpath)
        return item
    
    def append(self, name, tpathls=[]):
        self.add_to_tree(self.root, name, tpathls) 
    
    def OnSelChanged(self, evt):
        self.item = evt.GetItem()
        if self.item:
            i = self.item
            tpathls = []
            while 1:
                if not i or not i.IsOk() or not self.IsVisible(i):
                    break
                text = self.GetItemText(i)
                tpathls.append(text)
                i = self.GetItemParent(i)
            tpathls.reverse()
            tpath = '/' + '/'.join(tpathls)
            print 'path:', tpath
            
            self.parent.display_mailbox(tpath)
            
            
    def OnSize(self, evt):
        self.SetSize(self.GetSize())


