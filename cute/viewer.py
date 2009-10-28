# coding: utf-8
import os, sys
rundir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))).replace("\\", "/")
sys.path.insert(0, os.path.join(rundir, 'base'))
import wx
import logfile, config
from logfile import loginfo, logwarn, logerr
import viewhtml, mailparse
from common import load_bitmap, load_image
from picmenu import PicMenu

class MailViewFrame(wx.Frame):
    def __init__(self, parent, rundir, user, mailfile):
        self.rundir = rundir 
        self.bmpdir = self.rundir + "/bitmaps"
        self.mailfile = mailfile
        self.user = user
        
        wx.Frame.__init__(self, parent, title=u'查看邮件', size=(800,600))
        self.parent = parent
        
        self.make_menu()
        self.make_toolbar()
        self.make_viewer(mailfile)
        self.make_statusbar()
        
    def make_menu(self):
        self.ID_MENU_EXIT = wx.NewId()
        self.ID_MENU_SOURCE = wx.NewId()
        self.ID_MENU_REPLY = wx.NewId()
        self.ID_MENU_FORWARD = wx.NewId()
        
        self.menubar = wx.MenuBar()
        
        self.filemenu = PicMenu(self)
        self.filemenu.Append(self.ID_MENU_EXIT, u'退出', 'exit.png')
        self.menubar.Append(self.filemenu, u'文件')
        
        self.viewmenu = PicMenu(self)
        self.viewmenu.Append(self.ID_MENU_SOURCE, u'邮件原文', 'contents.png')
        self.menubar.Append(self.viewmenu, u'查看')
        
        self.mailmenu = PicMenu(self)
        self.mailmenu.Append(self.ID_MENU_REPLY, u'回复', 'mail_reply.png')
        self.mailmenu.Append(self.ID_MENU_FORWARD, u'转发', 'mail_send.png')
        self.menubar.Append(self.mailmenu, u'邮件')
        
        self.SetMenuBar(self.menubar)
        
        self.Bind(wx.EVT_MENU, self.OnFileExit, id=self.ID_MENU_EXIT)
        self.Bind(wx.EVT_MENU, self.OnViewSource, id=self.ID_MENU_SOURCE)
        self.Bind(wx.EVT_MENU, self.OnMailReply, id=self.ID_MENU_REPLY)
        self.Bind(wx.EVT_MENU, self.OnMailForward, id=self.ID_MENU_FORWARD)
    
    def make_toolbar(self):
        self.ID_TOOLBAR_REPLY = wx.NewId()
        self.ID_TOOLBAR_FORWARD = wx.NewId()
        
        self.toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.Size(48, 48), style=wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_TEXT)
        self.toolbar.SetToolBitmapSize(wx.Size(48,48))
    
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_REPLY, u'回复', load_bitmap(self.bmpdir+'/32/mail_reply.png'), shortHelp=u'回复邮件', longHelp=u'回复邮件')
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_FORWARD, u'转发', load_bitmap(self.bmpdir+'/32/mail_forward.png'), shortHelp=u'转发邮件', longHelp=u'转发邮件')
        
        self.toolbar.Realize()
        self.SetToolBar(self.toolbar)
        self.Bind(wx.EVT_TOOL, self.OnMailReply, id=self.ID_TOOLBAR_REPLY) 
        self.Bind(wx.EVT_TOOL, self.OnMailForward, id=self.ID_TOOLBAR_FORWARD) 
       
        
    def make_statusbar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(2)
        self.SetStatusWidths([-1, -2])
        
    def make_viewer(self, mailfile):
        text = ''
        ret = mailparse.decode_mail(mailfile)
        if ret:
            if ret['html']:
                text = ret['html']
            else:
                text = ret['plain']
        #panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.viewer = viewhtml.ViewHtml(self)
        self.viewer.set_text(text)
        sizer.Add(self.viewer, flag=wx.ALL|wx.EXPAND, border=0, proportion=1)
            
        if ret['attach']:
            self.attachctl = viewhtml.AttachListCtrl(self, self.rundir, wx.Size(-1,100))
            sizer.Add(self.attachctl, flag=wx.ALL|wx.EXPAND, border=0, proportion=0)
            homepath = os.path.join(config.cf.datadir, self.user)
            for item in ret['attach']:
                self.attachctl.add_file(item[0], {'home':homepath, 'file':mailfile, 'attach':item[0]})
        
        self.SetSizer(sizer)
        
    def OnFileExit(self, evt):
        self.Destroy()
    
    def OnViewSource(self, evt):
        pass
        
    def OnMailReply(self, evt):
        pass
    
    def OnMailForward(self, evt):
        pass
    
class TestApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)

    def OnInit(self):
        rundir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))).replace("\\", "/")
        mailfile = sys.argv[1]
        frame = MailViewFrame(None, rundir, 'zhaowei', mailfile)    
        frame.Show(True)
        self.SetTopWindow(frame)
        
        return True


if __name__ == '__main__':
    app = TestApp()
    app.MainLoop()
    
    
