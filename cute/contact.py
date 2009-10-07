# coding: utf-8
import os, sys
rundir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))).replace("\\", "/")
sys.path.insert(0, os.path.join(rundir, 'base'))

import linkman, logfile
import wx
from logfile import loginfo, logwarn, logerr
from common import load_bitmap, load_image
from picmenu import PicMenu

class ChatWindow(wx.Frame):
    def __init__(self, parent, rundir, title):
        wx.Frame.__init__(self, parent, -1, title=u'聊天: '+title, size=(500, 400))
        self.rundir = rundir

        self.make_menu()
        self.init()


    def init(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(1)
        self.SetStatusWidths([-1])
        
        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_3DSASH)
        p1 = wx.TextCtrl(self.splitter, -1, style=wx.TE_MULTILINE|wx.TE_READONLY) 
        self.input = wx.TextCtrl(self.splitter, -1, style=wx.TE_PROCESS_ENTER) 
        self.input.SetFocus()
        self.splitter.SetMinimumPaneSize(20)
        self.splitter.SplitHorizontally(p1, self.input, -80)

        self.input.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
       
    def make_menu(self):
        self.ID_MENU_EXIT = wx.NewId()
        
        self.menubar = wx.MenuBar()
        
        self.filemenu = PicMenu(self)
        self.filemenu.Append(self.ID_MENU_EXIT, u'退出', 'exit.png')
        self.menubar.Append(self.filemenu, u'文件')
        
        self.SetMenuBar(self.menubar)
        
        self.Bind(wx.EVT_MENU, self.OnFileExit, id=self.ID_MENU_EXIT)
        
    def OnFileExit(self, event):
        self.Destroy()

    def OnEnter(self, event):
        loginfo('enter ...')
        text = self.input.GetValue()
        loginfo('input:', text)
        self.input.SetValue('')

class ContactTree(wx.TreeCtrl):
    def __init__(self, parent, rundir, user):
        super(ContactTree, self).__init__(parent, wx.NewId(), 
                wx.Point(0, 0), wx.Size(200, 200), 
                style = wx.TR_DEFAULT_STYLE |wx.TR_HIDE_ROOT)
        
        self.rundir = rundir
        self.user   = user
        self.linkman = linkman.LinkMan(user)
        self.linkman.load() 

        self.init()

    def init(self):
        isz = (16,16)       
        il = wx.ImageList(isz[0], isz[1])

        self.contact = il.Add(load_bitmap(os.path.join(self.rundir, 'bitmaps/16/contact.png')))
        self.online  = il.Add(load_bitmap(os.path.join(self.rundir, 'bitmaps/16/online.png')))
        self.offline = il.Add(load_bitmap(os.path.join(self.rundir, 'bitmaps/16/offline.png')))
        self.SetImageList(il)
        self.il = il

        self.root = self.AddRoot("/")
        keys = self.linkman.groups['groupname']
        for k in keys:
            item = self.AppendItem(self.root, k)
            self.SetItemImage(item, self.contact, wx.TreeItemIcon_Normal)
            self.SetPyData(item, None)
            
            v = self.linkman.groups[k]
            for x in v:
                sub = self.AppendItem(item, x[0])
                self.SetPyData(sub, x)
                self.SetItemImage(sub, self.offline, wx.TreeItemIcon_Normal)
        
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)

    def OnActivate(self, event):
        item = event.GetItem()
        data = self.GetPyData(item)
        if data is None:
            return

        email = data[1]
        loginfo('email:', email) 

    def OnLeftDClick(self, event):
        pt = event.GetPosition()
        item, flags = self.HitTest(pt)
        data = self.GetPyData(item)
        loginfo('item data:', data)
        if data is None:
            loginfo('left double click data is None.')
            self.Expand(item)
            return

        frame = ChatWindow(self, self.rundir, data[0] + ' ' + data[1])
        frame.Show()

              
class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, size=(800, 600))

        sizer = wx.BoxSizer(wx.VERTICAL)
        x = ContactTree(self, os.path.dirname(os.getcwd()), 'zhaowei') 
        sizer.Add(x, 1, wx.ALL|wx.EXPAND, border=1)
        
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

def test():
    app = wx.PySimpleApp()
    frame = TestFrame()
    frame.Show()
    app.MainLoop()
    


if __name__ == '__main__':
    test()


