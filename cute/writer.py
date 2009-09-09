# coding: utf-8
import os, sys, time
import wx
import wx.richtext as rt
import wx.lib.sized_controls as sc
from picmenu import PicMenu
from common import load_bitmap, load_image
import images
import viewhtml
import createmail, config, dbope

class WriterFrame (wx.Frame):
    def __init__(self, parent, rundir, maildata):
        wx.Frame.__init__(self, parent, title=u'写邮件 ' + maildata['from'], size=(800,600))
        self.parent = parent 
        self.maildata = maildata
        self.rundir = rundir 
        self.bmpdir = self.rundir + "/bitmaps"
        self.header = {}
        self.attachlist = []

        self.make_menu()
        self.make_status()
         
        sizer = wx.BoxSizer(wx.VERTICAL)
        #x = self.make_toolbar()
        #sizer.Add(x, flag=wx.ALL|wx.EXPAND, border=0)
        self.make_toolbar()
        x = self.make_header(maildata)
        if x:
            sizer.Add(x, flag=wx.ALL|wx.EXPAND, border=0)
        x = self.make_writer_toolbar()
        sizer.Add(x, flag=wx.ALL|wx.EXPAND, border=0)
        
        self.splitter = wx.SplitterWindow(self, -1, style = wx.SP_LIVE_UPDATE)
        sizer.Add(self.splitter, flag=wx.ALL|wx.EXPAND, border=0, proportion=1)
        
        x = self.make_writer(self.splitter, maildata)
        #sizer.Add(x, flag=wx.ALL|wx.EXPAND, border=0, proportion=1)
        
        x = self.make_attach(self.splitter, maildata)
        #sizer.Add(x, flag=wx.ALL|wx.EXPAND, border=0, proportion=1)
        
        #self.splitter.SetMinimumPaneSize(20)
        self.splitter.SplitHorizontally(self.rtc, self.attach, -70)
        
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def make_menu(self):
        self.ID_MAIL_SEND = wx.NewId()
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
        self.mailmenu.Append(self.ID_MAIL_SAVE_DRAFT, u'保存为草稿', 'mail_send.png')
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
        self.ID_TOOLBAR_SAVE_DRAFT = wx.NewId()
        self.ID_TOOLBAR_ATTACH = wx.NewId()
        self.ID_TOOLBAR_LINKMAN = wx.NewId()
    
        self.toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.Size(48, 48), style=wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_TEXT)
        self.toolbar.SetToolBitmapSize(wx.Size(48,48))
    
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_SEND, u'发送邮件', load_bitmap(self.bmpdir+'/32/mail_send.png'), 
                shortHelp=u'发送邮件', longHelp=u'发送邮件')
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_SAVE_DRAFT, u'保存为草稿', load_bitmap(self.bmpdir+'/32/queue.png'), 
                shortHelp=u'保存到草稿箱', longHelp=u'保存到草稿箱')
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_ATTACH, u'附件', load_bitmap(self.bmpdir+'/32/attach.png'), 
                shortHelp=u'附件', longHelp=u'附件')
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(self.ID_TOOLBAR_LINKMAN, u'联系人', load_bitmap(self.bmpdir+'/32/identity.png'), 
                shortHelp=u'联系人', longHelp=u'联系人')

        self.toolbar.Realize()
        self.SetToolBar(self.toolbar)

        self.Bind(wx.EVT_TOOL, self.OnMailSend, id=self.ID_TOOLBAR_SEND)
        self.Bind(wx.EVT_TOOL, self.OnMailSaveDraft, id=self.ID_TOOLBAR_SAVE_DRAFT)
        self.Bind(wx.EVT_TOOL, self.OnInsertAttach, id=self.ID_TOOLBAR_ATTACH)
        self.Bind(wx.EVT_TOOL, self.OnLinkman, id=self.ID_TOOLBAR_LINKMAN)
     
    def make_header(self, maildata):
        #panel = sc.SizedPanel(self, -1)
        #panel.SetSizerType("form")
        panel = wx.Panel(self)
        sizer = wx.FlexGridSizer(0, 2, 0, 0)
        
        a = wx.StaticText(panel, -1, u'　主　题:')
        self.subject = wx.TextCtrl(panel, -1, maildata['subject'])
        wx.CallAfter(self.subject.SetInsertionPoint, 0)
        sizer.AddMany([(a, 0, wx.ALL|wx.EXPAND, 5), (self.subject, 0, wx.ALL|wx.EXPAND, 5)])
        a = wx.StaticText(panel, -1, u'　收件人:')
        self.mailto = wx.TextCtrl(panel, -1, maildata['to'])
        sizer.AddMany([(a, 0, wx.ALL|wx.EXPAND, 5), (self.mailto, 0, wx.ALL|wx.EXPAND, 5)])
       
        sizer.AddGrowableCol(1)
        panel.SetSizer(sizer) 
        return panel
        
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
                            shortHelpString=u"剪切"), self.ForwardEvent, self.ForwardEvent)
        doBind( self.writertb.AddTool(wx.ID_COPY, images._rt_copy.GetBitmap(),
                            shortHelpString=u"复制"), self.ForwardEvent, self.ForwardEvent)
        doBind( self.writertb.AddTool(wx.ID_PASTE, images._rt_paste.GetBitmap(),
                            shortHelpString=u"粘贴"), self.ForwardEvent, self.ForwardEvent)
        self.writertb.AddSeparator()
        doBind( self.writertb.AddTool(wx.ID_UNDO, images._rt_undo.GetBitmap(),
                            shortHelpString=u"撤销"), self.ForwardEvent, self.ForwardEvent)
        doBind( self.writertb.AddTool(wx.ID_REDO, images._rt_redo.GetBitmap(),
                            shortHelpString=u"恢复"), self.ForwardEvent, self.ForwardEvent)
        self.writertb.AddSeparator()
        doBind( self.writertb.AddTool(-1, images._rt_bold.GetBitmap(), isToggle=True,
                            shortHelpString=u"粗体"), self.OnBold, self.OnUpdateBold)
        doBind( self.writertb.AddTool(-1, images._rt_italic.GetBitmap(), isToggle=True,
                            shortHelpString=u"斜体"), self.OnItalic, self.OnUpdateItalic)
        doBind( self.writertb.AddTool(-1, images._rt_underline.GetBitmap(), isToggle=True,
                            shortHelpString=u"下划线"), self.OnUnderline, self.OnUpdateUnderline)
        self.writertb.AddSeparator()
        doBind( self.writertb.AddTool(-1, images._rt_alignleft.GetBitmap(), isToggle=True,
                            shortHelpString=u"左对齐"), self.OnAlignLeft, self.OnUpdateAlignLeft)
        doBind( self.writertb.AddTool(-1, images._rt_centre.GetBitmap(), isToggle=True,
                            shortHelpString=u"居中"), self.OnAlignCenter, self.OnUpdateAlignCenter)
        doBind( self.writertb.AddTool(-1, images._rt_alignright.GetBitmap(), isToggle=True,
                            shortHelpString=u"右对齐"), self.OnAlignRight, self.OnUpdateAlignRight)
        self.writertb.AddSeparator()
        doBind( self.writertb.AddTool(-1, images._rt_indentless.GetBitmap(),
                            shortHelpString=u"向左缩进"), self.OnIndentLess)
        doBind( self.writertb.AddTool(-1, images._rt_indentmore.GetBitmap(),
                            shortHelpString=u"向右缩进"), self.OnIndentMore)
        self.writertb.AddSeparator()
        doBind( self.writertb.AddTool(-1, images._rt_font.GetBitmap(),
                            shortHelpString=u"字体"), self.OnFont)
        doBind( self.writertb.AddTool(-1, load_bitmap(self.bmpdir + '/16/colorize.png'),
                            shortHelpString=u"字体颜色"), self.OnColour)

        doBind( self.writertb.AddTool(-1, load_bitmap(self.bmpdir + '/16/img2.png'), 
                            shortHelpString=u"插入图片"), self.OnInsertImage)
        self.writertb.Realize()
        
        return tbpanel
            
            
    def make_writer(self, parent, maildata):
        self.rtc =  rt.RichTextCtrl(parent, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)
        self.rtc.Newline()
        self.rtc.WriteText(maildata['text'])
        self.rtc.MoveHome()
        wx.CallAfter(self.rtc.SetFocus)
        return self.rtc
    
    def make_attach(self, parent, maildata):
        self.attach = viewhtml.AttachListCtrl(parent, self.rundir, wx.Size(-1,100))
        return self.attach
       
       
    def create_mail(self, path):
        handler = rt.RichTextHTMLHandler()
        handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_MEMORY)
        handler.SetFontSizeMapping([7,9,11,12,14,22,100])

        import cStringIO
        htmlstream = cStringIO.StringIO()
        if not handler.SaveStream(self.rtc.GetBuffer(), htmlstream):
            return
        
        self.header['from'] = self.maildata['from']
        self.header['to'] = self.maildata['to']
        self.header['subject'] = self.maildata['subject']
        creator = createmail.CreateEmail('', htmlstream.getvalue(), self.attachlist, self.header) 
        s = creator.generate_email()
        
        f = open(path, 'w')
        f.write(s)
        f.close()
        
        aa = []
        for x in self.attachlist:
            aa.append(x + '::')
        self.maildata['size'] = len(s)
        self.maildata['date'] = '%d-%02d-%02d %02d:%02d:%02d' % (time.localtime()[:6])
        self.maildata['attach'] = '||'.join(aa)
    
    def save_mail(self, box):
        tostr = self.mailto.GetValue().strip()
        self.maildata['to'] = tostr.split(',')
        self.maildata['subject'] = self.subject.GetValue().strip()

        s = str(time.time())+'.eml'
        filedir = os.path.join(config.cf.datadir, self.maildata['user'], box)
        filepath = os.path.join(filedir, s)
        print 'save file:', filepath
        if not os.path.isdir(filedir):
            os.mkdir(filedir)
        self.create_mail(filepath)
        self.maildata['filepath'] = filepath
        sql = "insert into mailinfo(filename,subject,mailfrom,mailto,size,ctime,date,attach,mailbox) values ('%s','%s','%s','%s',%d,%s,'%s','%s','%s')" % \
              (s, self.maildata['subject'], self.maildata['from'], ','.join(self.maildata['to']), self.maildata['size'],
               'datetime()', self.maildata['date'], self.maildata['attach'], box)
        print sql 
        db = dbope.openuser(config.cf, self.maildata['user'])
        db.execute(sql)
        ret = db.query("select last_insert_rowid();", False)
        rowid = ret[0][0]
        db.close()

        self.maildata['id'] = rowid


    def OnMailSend(self, evt):
        self.save_mail('send') 
        msg = {'name':self.maildata['user'], 'task':'sendmail', 'to':self.maildata['to'], 
               'from':self.maildata['from'], 'path':self.maildata['filepath']}
        #sendmail.sendfile(self.maildata)
        if self.maildata.has_key('id'):
            self.parent.load_db_one(self.maildata['user'], self.maildata['id'])
     
        config.taskq.put(msg)

    def OnMailSaveDraft(self, evt):
        self.save_mail('draft') 
        
        if self.maildata.has_key('id'):
            self.parent.load_db_one(self.maildata['user'], self.maildata['id'])
        
    def OnMailExit(self, evt):
        self.Destroy()

    def OnEditCopy(self, evt):
        self.ForwardEvent(evt)

    def OnEditPaste(self, evt):
        self.ForwardEvent(evt)

    def OnEditCut(self, evt):
        self.ForwardEvent(evt)

    def OnEditChooseAll(self, evt):
        self.ForwardEvent(evt)

    def OnInsertAttach(self, evt):
        dlg = wx.FileDialog(
            self, message=u"选择附件",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=u"所有文件 (*.*)|*.*",
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                print 'attach:', path
                
                self.attachlist.append(path)
                self.attach.add_file(os.path.basename(path), {'path':path})
        dlg.Destroy()
      
    def OnDeleteAttach(self, evt):
        pass

    def OnOptionReceipt(self, evt):
        self.header['Disposition-Notification-To'] = self.maildata['from']

    def OnLinkman(self, evt):
        pass

    # ------------- RichTextCtrl events
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
                if self.rtc.HasSelection():
                    attr.SetFlags(rt.TEXT_ATTR_FONT)
                    attr.SetFont(font)
                    r = self.rtc.GetSelectionRange()
                    self.rtc.SetStyle(r, attr)
                else:
                    self.rtc.SetFont(font)
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
        
    def OnInsertImage(self, evt):
        dlg = wx.FileDialog(
            self, message=u"选择图片",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=u"jpg图片 (*.jpg)|*.jpg|bmp图片 (*.bmp)|*.bmp|" \
                     u"gif图片 (*.gif)|*.gif|png图片文件 (*.png)|*.png|" \
                     u"jpeg图片文件 (*.jpeg)|*.jpeg|所有文件 (*.*)|*.*",
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                pic = load_image(path)
                self.rtc.WriteImage(pic)
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
        data = {'subject':'', 'from':'', 'to':'', 'text':''}
        rundir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))).replace("\\", "/")
        frame = WriterFrame(None, rundir, data)    
        frame.Show(True)
        self.SetTopWindow(frame)
        
        return True


if __name__ == '__main__':
    app = TestApp()
    app.MainLoop()


