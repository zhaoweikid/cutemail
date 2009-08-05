# coding: utf-8
import os, sys
import wx
import wx.richtext as rt
from picmenu import PicMenu
import common
import images

class WriterWin (wx.Frame):
    def __init__(self, parent, rundir):
        wx.Frame.__init__(self, parent, title=u'写邮件', size=(800,600))
        
        self.rundir = rundir 
        self.bmpdir = self.rundir + "/bitmaps"

        
        self.make_menu()
        self.make_status()
         
        sizer = wx.BoxSizer(wx.VERTICAL)
        x = self.make_toolbar()
        sizer.Add(x, flag=wx.ALL|wx.EXPAND, border=0)
        x = self.make_writer_toolbar()
        sizer.Add(x, flag=wx.ALL|wx.EXPAND, border=0)
        x = self.make_writer()
        sizer.Add(x, flag=wx.ALL|wx.EXPAND, border=0)
        
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

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
        client = wx.Panel(self)
        #client.SetBackgroundColour(wx.NamedColour("WHITE"))
        
        self.ID_TOOLBAR_SEND = wx.NewId()
        self.ID_TOOLBAR_SAVE_SENDBOX = wx.NewId()
        self.ID_TOOLBAR_SAVE_DRAFT = wx.NewId()
        self.ID_TOOLBAR_ATTACH = wx.NewId()
        self.ID_TOOLBAR_LINKMAN = wx.NewId()
    
        self.toolbar = wx.ToolBar(client, -1, wx.DefaultPosition, wx.Size(48, 48), wx.TB_HORIZONTAL|wx.TB_FLAT)
        
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.toolbar, flag=wx.ALL|wx.EXPAND)
        client.SetSizer(sizer1)
        
        self.toolbar.SetToolBitmapSize(wx.Size(48,48))
    
        self.toolbar.AddSimpleTool(self.ID_TOOLBAR_SEND, common.load_image(self.bmpdir+'/32/mail_send.png'), u'发送邮件', u'发送邮件')
        self.toolbar.AddSimpleTool(self.ID_TOOLBAR_SAVE_SENDBOX, common.load_image(self.bmpdir+'/32/mail_new.png'), u'保存到发件箱', u'保存到发件箱')
        self.toolbar.AddSimpleTool(self.ID_TOOLBAR_SAVE_DRAFT, common.load_image(self.bmpdir+'/32/mail_new.png'), u'保存到草稿箱', u'保存到草稿箱')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(self.ID_TOOLBAR_ATTACH, common.load_image(self.bmpdir+'/32/mail_new.png'), u'附件', u'附件')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(self.ID_TOOLBAR_LINKMAN, common.load_image(self.bmpdir+'/32/chat.png'), u'联系人', u'联系人')

        self.toolbar.Realize()
        #self.SetToolBar(self.toolbar)

        self.Bind(wx.EVT_TOOL, self.OnMailSend, id=self.ID_TOOLBAR_SEND)
        self.Bind(wx.EVT_TOOL, self.OnMailSaveSendbox, id=self.ID_TOOLBAR_SAVE_SENDBOX)
        self.Bind(wx.EVT_TOOL, self.OnMailSaveDraft, id=self.ID_TOOLBAR_SAVE_DRAFT)
        self.Bind(wx.EVT_TOOL, self.OnInsertAttach, id=self.ID_TOOLBAR_ATTACH)
        self.Bind(wx.EVT_TOOL, self.OnLinkman, id=self.ID_TOOLBAR_LINKMAN)
        
        return client

    def make_status(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.SetStatusWidths([-1, -2, -2])


    def make_writer_toolbar(self):
        def doBind(item, handler, updateUI=None):
            self.Bind(wx.EVT_TOOL, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
                
        
        tbpanel = wx.Panel(self)
        tbpanel.SetBackgroundColour(wx.NamedColour("WHITE"))
        
        self.writertb = wx.ToolBar(tbpanel, style=wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_TEXT)
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.writertb, flag=wx.ALL|wx.EXPAND)
        tbpanel.SetSizer(sizer1)
            
         
        doBind( self.writertb.AddTool(wx.ID_CUT, images._rt_cut.GetBitmap(),
                            shortHelpString="Cut"), self.ForwardEvent, self.ForwardEvent)
        doBind( self.writertb.AddTool(wx.ID_COPY, images._rt_copy.GetBitmap(),
                            shortHelpString="Copy"), self.ForwardEvent, self.ForwardEvent)
        doBind( self.writertb.AddTool(wx.ID_PASTE, images._rt_paste.GetBitmap(),
                            shortHelpString="Paste"), self.ForwardEvent, self.ForwardEvent)
        self.writertb.AddSeparator()
        doBind( self.writertb.AddTool(wx.ID_UNDO, images._rt_undo.GetBitmap(),
                            shortHelpString="Undo"), self.ForwardEvent, self.ForwardEvent)
        doBind( self.writertb.AddTool(wx.ID_REDO, images._rt_redo.GetBitmap(),
                            shortHelpString="Redo"), self.ForwardEvent, self.ForwardEvent)
        self.writertb.AddSeparator()
        doBind( self.writertb.AddTool(-1, images._rt_bold.GetBitmap(), isToggle=True,
                            shortHelpString="Bold"), self.OnBold, self.OnUpdateBold)
        doBind( self.writertb.AddTool(-1, images._rt_italic.GetBitmap(), isToggle=True,
                            shortHelpString="Italic"), self.OnItalic, self.OnUpdateItalic)
        doBind( self.writertb.AddTool(-1, images._rt_underline.GetBitmap(), isToggle=True,
                            shortHelpString="Underline"), self.OnUnderline, self.OnUpdateUnderline)
        self.writertb.AddSeparator()
        doBind( self.writertb.AddTool(-1, images._rt_alignleft.GetBitmap(), isToggle=True,
                            shortHelpString="Align Left"), self.OnAlignLeft, self.OnUpdateAlignLeft)
        doBind( self.writertb.AddTool(-1, images._rt_centre.GetBitmap(), isToggle=True,
                            shortHelpString="Center"), self.OnAlignCenter, self.OnUpdateAlignCenter)
        doBind( self.writertb.AddTool(-1, images._rt_alignright.GetBitmap(), isToggle=True,
                            shortHelpString="Align Right"), self.OnAlignRight, self.OnUpdateAlignRight)
        self.writertb.AddSeparator()
        doBind( self.writertb.AddTool(-1, images._rt_indentless.GetBitmap(),
                            shortHelpString="Indent Less"), self.OnIndentLess)
        doBind( self.writertb.AddTool(-1, images._rt_indentmore.GetBitmap(),
                            shortHelpString="Indent More"), self.OnIndentMore)
        self.writertb.AddSeparator()
        doBind( self.writertb.AddTool(-1, images._rt_font.GetBitmap(),
                            shortHelpString="Font"), self.OnFont)
        doBind( self.writertb.AddTool(-1, images._rt_colour.GetBitmap(),
                            shortHelpString="Font Colour"), self.OnColour)

        self.writertb.Realize()
        
        return tbpanel
            
            
    def make_writer(self):
        wpanel = wx.Panel(self)
        wpanel.SetBackgroundColour(wx.NamedColour("WHITE"))
        self.rtc =  rt.RichTextCtrl(wpanel, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)
        wx.CallAfter(self.rtc.SetFocus)
        
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.rtc, flag=wx.ALL|wx.EXPAND, border=1)
        wpanel.SetSizer(sizer1)
        
        return wpanel
        
        
    def OnToolClick(self, evt):
        pass
    
    def OnToolRClick(self, evt):
        pass
    
    def OnToolEnter(self, evt):
        pass
    
    def OnClearSB(self, evt):
        pass
        
        

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

    # -------------
    def OnBold(self, evt):
        self.rtc.ApplyBoldToSelection()
        
    def OnItalic(self, evt): 
        self.rtc.ApplyItalicToSelection()
        
    def OnUnderline(self, evt):
        self.rtc.ApplyUnderlineToSelection()
        
    def OnAlignLeft(self, evt):
        self.rtc.ApplyAlignmentToSelection(rt.TEXT_ALIGNMENT_LEFT)
        
    def OnAlignRight(self, evt):
        self.rtc.ApplyAlignmentToSelection(rt.TEXT_ALIGNMENT_RIGHT)
        
    def OnAlignCenter(self, evt):
        self.rtc.ApplyAlignmentToSelection(rt.TEXT_ALIGNMENT_CENTRE)
        
    def OnIndentMore(self, evt):
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetLeftIndent(attr.GetLeftIndent() + 100)
            attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
            self.rtc.SetStyle(r, attr)
       
        
    def OnIndentLess(self, evt):
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

        if attr.GetLeftIndent() >= 100:
            attr.SetLeftIndent(attr.GetLeftIndent() - 100)
            attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
            self.rtc.SetStyle(r, attr)

        
    def OnParagraphSpacingMore(self, evt):
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() + 20);
            attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
            self.rtc.SetStyle(r, attr)

        
    def OnParagraphSpacingLess(self, evt):
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            if attr.GetParagraphSpacingAfter() >= 20:
                attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() - 20);
                attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
                self.rtc.SetStyle(r, attr)

        
    def OnLineSpacingSingle(self, evt): 
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(10)
            self.rtc.SetStyle(r, attr)
 
                
    def OnLineSpacingHalf(self, evt):
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(15)
            self.rtc.SetStyle(r, attr)

        
    def OnLineSpacingDouble(self, evt):
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(20)
            self.rtc.SetStyle(r, attr)


    def OnFont(self, evt):
        if not self.rtc.HasSelection():
            return

        r = self.rtc.GetSelectionRange()
        fontData = wx.FontData()
        fontData.EnableEffects(False)
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_FONT)
        if self.rtc.GetStyle(self.rtc.GetInsertionPoint(), attr):
            fontData.SetInitialFont(attr.GetFont())

        dlg = wx.FontDialog(self, fontData)
        if dlg.ShowModal() == wx.ID_OK:
            fontData = dlg.GetFontData()
            font = fontData.GetChosenFont()
            if font:
                attr.SetFlags(rt.TEXT_ATTR_FONT)
                attr.SetFont(font)
                self.rtc.SetStyle(r, attr)
        dlg.Destroy()


    def OnColour(self, evt):
        colourData = wx.ColourData()
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_TEXT_COLOUR)
        if self.rtc.GetStyle(self.rtc.GetInsertionPoint(), attr):
            colourData.SetColour(attr.GetTextColour())

        dlg = wx.ColourDialog(self, colourData)
        if dlg.ShowModal() == wx.ID_OK:
            colourData = dlg.GetColourData()
            colour = colourData.GetColour()
            if colour:
                if not self.rtc.HasSelection():
                    self.rtc.BeginTextColour(colour)
                else:
                    r = self.rtc.GetSelectionRange()
                    attr.SetFlags(rt.TEXT_ATTR_TEXT_COLOUR)
                    attr.SetTextColour(colour)
                    self.rtc.SetStyle(r, attr)
        dlg.Destroy()
        


    def OnUpdateBold(self, evt):
        evt.Check(self.rtc.IsSelectionBold())
    
    def OnUpdateItalic(self, evt): 
        evt.Check(self.rtc.IsSelectionItalics())
    
    def OnUpdateUnderline(self, evt): 
        evt.Check(self.rtc.IsSelectionUnderlined())
    
    def OnUpdateAlignLeft(self, evt):
        evt.Check(self.rtc.IsSelectionAligned(rt.TEXT_ALIGNMENT_LEFT))
        
    def OnUpdateAlignCenter(self, evt):
        evt.Check(self.rtc.IsSelectionAligned(rt.TEXT_ALIGNMENT_CENTRE))
        
    def OnUpdateAlignRight(self, evt):
        evt.Check(self.rtc.IsSelectionAligned(rt.TEXT_ALIGNMENT_RIGHT))

    
    def ForwardEvent(self, evt):
        # The RichTextCtrl can handle menu and update events for undo,
        # redo, cut, copy, paste, delete, and select all, so just
        # forward the event to it.
        self.rtc.ProcessEvent(evt)



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


