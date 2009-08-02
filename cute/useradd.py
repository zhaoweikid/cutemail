# coding: utf-8
import os, sys
import wx
import wx.wizard as wiz
import wx.lib.sized_controls as sc

tmpuser = {}

def make_page_title(wizPg, title):
    sizer = wx.BoxSizer(wx.VERTICAL)
    wizPg.SetSizer(sizer)
    title = wx.StaticText(wizPg, -1, title)
    #title.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
    sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND|wx.ALL, 5)
    return sizer

class UsernamePage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)
        
        panel = sc.SizedPanel(self, -1)
        panel.SetSizerType("form")
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(self, -1, u'新建用户')
        
        sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        
        
        wx.StaticText(panel, -1, '') 
        wx.StaticText(panel, -1, u'在使用CuteMail之前，你需要先添加账户，\n每个账户对应一个邮件地址。')
        
        wx.StaticText(panel, -1, u'请输入用户名:')
        self.boxname = wx.TextCtrl(panel, -1, size=(200,-1))
        
        wx.StaticText(panel, -1, '') 
        wx.StaticText(panel, -1, u'您需要设置一个该邮箱的信件存储位置，不填表示使用默认设置')
        
        wx.StaticText(panel, -1, u'请输入存储路径:')
        self.storage = wx.TextCtrl(panel, -1, size=(200,-1))
        
        wx.StaticText(panel, -1, '') 
        wx.StaticText(panel, -1, u'请输入您的姓名，这将出现在您发送的邮件的发件人中。')
        
        wx.StaticText(panel, -1, u'姓名:')
        self.username = wx.TextCtrl(panel, -1, size=(200,-1))
        
        wx.StaticText(panel, -1, '') 
        wx.StaticText(panel, -1, u'请输入您要使用的邮箱')
        
        wx.StaticText(panel, -1, u'邮箱地址:')
        self.email = wx.TextCtrl(panel, -1, size=(200,-1))
        
        self.SetAutoLayout(True)
 

class EmailPage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)

        panel = sc.SizedPanel(self, -1)
        panel.SetSizerType("form")
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(self, -1, u'输入邮件地址信息')
        
        sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        
        
        wx.StaticText(panel, -1, '') 
        wx.StaticText(panel, -1, u'请输入您的姓名，这将出现在您发送的邮件的发件人中。')
        
        wx.StaticText(panel, -1, u'姓名:')
        self.username = wx.TextCtrl(panel, -1, size=(200,-1))
        
        wx.StaticText(panel, -1, '') 
        wx.StaticText(panel, -1, u'请输入您要使用的邮箱')
        
        wx.StaticText(panel, -1, u'邮箱地址:')
        self.email = wx.TextCtrl(panel, -1, size=(200,-1))
        
        self.SetAutoLayout(True)

class ServerPage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)

        panel = sc.SizedPanel(self, -1)
        panel.SetSizerType("form")
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(self, -1, u'选择邮件收取方式')
        
        sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        
        
        wx.StaticText(panel, -1, '') 
        wx.StaticText(panel, -1, u'请输入您使用的pop3服务器地址，比如pop3.163.com')
        
        wx.StaticText(panel, -1, u'POP3服务器地址:')
        self.pop3server = wx.TextCtrl(panel, -1, size=(200,-1))
        
        wx.StaticText(panel, -1, '') 
        wx.StaticText(panel, -1, u'请输入POP3账户密码')
        
        wx.StaticText(panel, -1, u'POP3密码:')
        self.pop3pass = wx.TextCtrl(panel, -1, size=(200,-1))
        
        wx.StaticText(panel, -1, '') 
        wx.StaticText(panel, -1, u'请输入您使用的SMTP服务器地址，比如smtp.163.com')
        
        wx.StaticText(panel, -1, u'SMTP服务器地址:')
        self.smtpserver = wx.TextCtrl(panel, -1, size=(200,-1))
        
        wx.StaticText(panel, -1, '') 
        wx.StaticText(panel, -1, u'请输入SMTP账户密码，不填写表示不需要密码')
        
        wx.StaticText(panel, -1, u'SMTP密码:')
        self.smtppass = wx.TextCtrl(panel, -1, size=(200,-1))
        
        self.SetAutoLayout(True)

class TestPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
    

        b = wx.Button(self, -1, "Run Simple Wizard", pos=(50, 50))
        self.Bind(wx.EVT_BUTTON, self.OnRunSimpleWizard, b)
    
    def OnRunSimpleWizard(self, evt):
        import images
        print 'run simple wizard...'
        wizard = wiz.Wizard(self, -1, u"新建用户向导", images.WizTest1.GetBitmap())

        page1 = UsernamePage(wizard, "page 1")
        page2 = EmailPage(wizard, "page 2")
        page3 = ServerPage(wizard, "page 3")
    
        wizard.FitToPage(page1)
    
        wiz.WizardPageSimple_Chain(page1, page2)
        wiz.WizardPageSimple_Chain(page2, page3)
    
        wizard.GetPageAreaSizer().Add(page1)
        ret = wizard.RunWizard(page1)
        print 'ret:', ret
        if ret:
            wx.MessageBox("Wizard completed successfully", "That's all folks!")
            print 'boxname:', page1.boxname.GetValue()
            print 'storage:', page1.storage.GetValue()
        else:
            wx.MessageBox("Wizard was cancelled", "That's all folks!")
    


def test(frame):
    win = TestPanel(frame)
    return win

