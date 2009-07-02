# coding: utf-8
import os, sys
import wx
import  wx.wizard as wiz

def make_page_title(wizPg, title):
    sizer = wx.BoxSizer(wx.VERTICAL)
    wizPg.SetSizer(sizer)
    title = wx.StaticText(wizPg, -1, title)
    title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
    sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND|wx.ALL, 5)
    return sizer

class WelcomePage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)
        self.sizer = make_page_title(self, title)

class UsernamePage(wiz.WizardPageSimple):
    pass

class EmailPage(wiz.WizardPageSimple):
    pass


class ServerPage(wiz.WizardPageSimple):
    pass



def test(frame):
    pass

