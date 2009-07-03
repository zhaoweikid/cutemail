# coding: utf-8
import os, sys
import wx
import wx.wizard as wiz

def make_page_title(wizPg, title):
    sizer = wx.BoxSizer(wx.VERTICAL)
    wizPg.SetSizer(sizer)
    title = wx.StaticText(wizPg, -1, title)
    #title.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
    sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND|wx.ALL, 5)
    return sizer

class WelcomePage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        title = wx.StaticText(self, -1, u'欢迎使用CuteMail')
        #title.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 5)
        content = wx.StaticText(self, -1, u'在使用CuteMail之前，你需要先添加账户，每个账户对应一个邮件地址。\nCuteMail将为你管理这个邮箱。')
        sizer.Add(content, -1, wx.EXPAND|wx.ALL, 5)
 

class UsernamePage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)
         
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        title = wx.StaticText(self, -1, u'建立新账户')
        #title.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 5)
        content = wx.StaticText(self, -1, u'输入一个用户，用来标识此邮箱，CuteMail需要用不同的用户名来管理多账户。')
        sizer.Add(content, -1, wx.EXPAND|wx.ALL, 5)
        
        


class EmailPage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)
        self.sizer = make_page_title(self, title)


class ServerPage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)
       	self.sizer = make_page_title(self, title)


class TestPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
    

        b = wx.Button(self, -1, "Run Simple Wizard", pos=(50, 50))
        self.Bind(wx.EVT_BUTTON, self.OnRunSimpleWizard, b)
    
    def OnRunSimpleWizard(self, evt):
        import images
        print 'run simple wizard...'
        wizard = wiz.Wizard(self, -1, "Simple Wizard", images.getWizTest1Bitmap())
        page1 = WelcomePage(wizard, "page 1")
        page2 = UsernamePage(wizard, "page 2")
        page3 = EmailPage(wizard, "page 3")
        page4 = ServerPage(wizard, "page 4")
    
        wizard.FitToPage(page1)
        page4.sizer.Add(wx.StaticText(page4, -1, "\nThis is the last page."))
    
        wiz.WizardPageSimple_Chain(page1, page2)
        wiz.WizardPageSimple_Chain(page2, page3)
        wiz.WizardPageSimple_Chain(page3, page4)
    
        wizard.GetPageAreaSizer().Add(page1)
        if wizard.RunWizard(page1):
            wx.MessageBox("Wizard completed successfully", "That's all folks!")
        else:
            wx.MessageBox("Wizard was cancelled", "That's all folks!")
    


def test(frame):
    win = TestPanel(frame)
    return win

