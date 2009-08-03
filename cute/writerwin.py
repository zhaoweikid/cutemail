# coding: utf-8
import os, sys
import wx
import wx.richtext as rt
from picmenu import PicMenu
import common


class WriterWin (wx.Frame):
    def __init__(self, parent, rundir):
        wx.Frame.__init__(self, parent, title=u'写邮件')
        
        self.rundir = rundir 
        self.bmpdir = self.rundir + "/bitmaps"

        self.make_menu()
        self.make_toolbar()
        self.make_status()
        self.make_writer()

    def make_menu(self):
        self.ID_MAIL_SEND = wx.NewId()
        self.ID_MAIL_SAVE_SENDBOX = wx.NewId()
        self.ID_MAIL_SAVE_DRAFT = wx.NewId()
        self.ID_MAIL_EXIT = wx.NewId()

        self.ID_EDIT_COPY = wx.NewId()
        self.ID_EDIT_PASTE = wx.NewId()
        self.ID_EDIT_CUT = wx.NewId()
        self.ID_EDIT_CHOOSE_ALL = wx.NewId()

        self.ID_INSERT_ATTACH = wx.NewId()

        self.ID_OPTION_RECEIPT = wx.NewId()

        self.menubar = wx.MenuBar()        

        self.mailmenu = PicMenu(self)
        self.mailmenu.Append(self.ID_MAIL_SEND, u'发送', 'mail_send.png')
        self.mailmenu.Append(self.ID_MAIL_SAVE_SENDBOX, u'保存到发件箱', 'mail_send.png')
        self.mailmenu.Append(self.ID_MAIL_SAVE_DRAFT, u'保存到草稿箱', 'mail_send.png')
        self.mailmenu.AppendSeparator()
        self.mailmenu.Append(self.ID_MAIL_EXIT, u'退出', 'exit.png')
        self.menubar.Append(self.mailmenu, u'邮件')

        self.editmenu = PicMenu(self)
        self.editmenu.Append(self.ID_EDIT_COPY, u'复制', 'editcopy.png')
        self.editmenu.Append(self.ID_EDIT_PASTE, u'粘贴', 'editcopy.png')
        self.editmenu.Append(self.ID_EDIT_CUT, u'剪切', 'editcut.png')
        self.editmenu.Append(self.ID_EDIT_CHOOSE_ALL, u'全选', 'check.png')
        self.menubar.Append(self.editmenu, u'编辑')

        self.insertmenu = PicMenu(self)
        self.insertmenu.Append(self.ID_INSERT_ATTACH, u'附件', 'attach.png')
        self.menubar.Append(self.insertmenu, u'插入')
        
        self.optionmenu = PicMenu(self)
        self.optionmenu.Append(self.ID_OPTION_RECEIPT, u'请求收条', 'note.png')
        self.menubar.Append(self.optionmenu, u'选项')

        self.SetMenuBar(self.menubar)

    
        self.Bind(wx.EVT_MENU, self.OnMailSend, id=self.ID_MAIL_SEND)     
        self.Bind(wx.EVT_MENU, self.OnMailSaveSendbox, id=self.ID_MAIL_SAVE_SENDBOX)     
        self.Bind(wx.EVT_MENU, self.OnMailSaveDraft, id=self.ID_MAIL_SAVE_DRAFT)     
        self.Bind(wx.EVT_MENU, self.OnMailExit, id=self.ID_MAIL_EXIT)     
        self.Bind(wx.EVT_MENU, self.OnEditCopy, id=self.ID_EDIT_COPY)     
        self.Bind(wx.EVT_MENU, self.OnEditPaste, id=self.ID_EDIT_PASTE)     
        self.Bind(wx.EVT_MENU, self.OnEditCut, id=self.ID_EDIT_CUT)     
        self.Bind(wx.EVT_MENU, self.OnEditChooseAll, id=self.ID_EDIT_CHOOSE_ALL)     
        self.Bind(wx.EVT_MENU, self.OnInsertAttach, id=self.ID_INSERT_ATTACH)     
        self.Bind(wx.EVT_MENU, self.OnOptionReceipt, id=self.ID_OPTION_RECEIPT)     
    
    def make_toolbar(self):
        self.ID_TOOLBAR_SEND = wx.NewId()
        self.ID_TOOLBAR_SAVE_SENDBOX = wx.NewId()
        self.ID_TOOLBAR_SAVE_DRAFT = wx.NewId()
        self.ID_TOOLBAR_ATTACH = wx.NewId()
        self.ID_TOOLBAR_LINKMAN = wx.NewId()
    
        self.toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.Size(48, 48), wx.TB_HORIZONTAL|wx.TB_FLAT) 
        self.toolbar.SetToolBitmapSize(wx.Size(48,48))
    
        self.toolbar.AddSimpleTool(self.ID_TOOLBAR_SEND, common.load_image(self.bmpdir+'/32/mail_send.png'), u'发送邮件', u'发送邮件')
        self.toolbar.AddSimpleTool(self.ID_TOOLBAR_SAVE_SENDBOX, common.load_image(self.bmpdir+'/32/mail_new.png'), u'保存到发件箱', u'保存到发件箱')
        self.toolbar.AddSimpleTool(self.ID_TOOLBAR_SAVE_DRAFT, common.load_image(self.bmpdir+'/32/mail_new.png'), u'保存到草稿箱', u'保存到草稿箱')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(self.ID_TOOLBAR_ATTACH, common.load_image(self.bmpdir+'/32/mail_new.png'), u'附件', u'附件')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(self.ID_TOOLBAR_LINKMAN, common.load_image(self.bmpdir+'/32/chat.png'), u'联系人', u'联系人')

        self.toolbar.Realize()
        self.SetToolBar(self.toolbar)

        self.Bind(wx.EVT_TOOL, self.OnMailSend, id=self.ID_TOOLBAR_SEND)
        self.Bind(wx.EVT_TOOL, self.OnMailSaveSendbox, id=self.ID_TOOLBAR_SAVE_SENDBOX)
        self.Bind(wx.EVT_TOOL, self.OnMailSaveDraft, id=self.ID_TOOLBAR_SAVE_DRAFT)
        self.Bind(wx.EVT_TOOL, self.OnInsertAttach, id=self.ID_TOOLBAR_ATTACH)
        self.Bind(wx.EVT_TOOL, self.OnLinkman, id=self.ID_TOOLBAR_LINKMAN)


    def make_status(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.SetStatusWidths([-1, -2, -2])


    def make_writer(self):
        self.rtc =  rt.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)        
        wx.CallAfter(self.rtc.SetFocus)
        
        

    def OnMailSend(self, evt):
        pass
    def OnMailSaveSendbox(self, evt):
        pass
    def OnMailSaveDraft(self, evt):
        pass
    def OnMailExit(self, evt):
        pass
    def OnEditCopy(self, evt):
        pass
    def OnEditPaste(self, evt):
        pass
    def OnEditCut(self, evt):
        pass
    def OnEditChooseAll(self, evt):
        pass
    def OnInsertAttach(self, evt):
        pass
    def OnOptionReceipt(self, evt):
        pass
    def OnLinkman(self, evt):
        pass


class TestApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)

    def OnInit(self):

        rundir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))).replace("\\", "/")
        frame = WriterWin(None, rundir)    
        frame.Show(True)
        self.SetTopWindow(frame)
        
        return True


if __name__ == '__main__':
    app = TestApp()
    app.MainLoop()


