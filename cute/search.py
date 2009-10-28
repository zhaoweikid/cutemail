# coding=utf-8
import os, sys
import wx
import wx.lib.sized_controls as sc
import config, logfile
from logfile import loginfo, logwarn, logerr

class SearchDialog(sc.SizedDialog):
    def __init__(self, parent, user):
        sc.SizedDialog.__init__(self, None, -1, u"信件搜索", 
                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent
        self.user = user


class MailSearchCtrl(wx.SearchCtrl):
    maxSearches = 5
    
    def __init__(self, parent, id=-1, value="",
                 pos=wx.DefaultPosition, size=wx.DefaultSize, style=0,
                 doSearch=None):
        style |= wx.TE_PROCESS_ENTER
        wx.SearchCtrl.__init__(self, parent, id, value, pos, size, style)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnTextEntered)
        self.Bind(wx.EVT_MENU_RANGE, self.OnMenuItem, id=1, id2=self.maxSearches)
        self.doSearch = doSearch
        self.searches = []

    def OnTextEntered(self, evt):
        text = self.GetValue()
        if self.doSearch(text):
            self.searches.append(text)
            if len(self.searches) > self.maxSearches:
                del self.searches[0]
            self.SetMenu(self.MakeMenu())            
        self.SetValue("")

    def OnMenuItem(self, evt):
        text = self.searches[evt.GetId()-1]
        self.doSearch(text)
        
    def MakeMenu(self):
        menu = wx.Menu()
        item = menu.Append(-1, "Recent Searches")
        item.Enable(False)
        for idx, txt in enumerate(self.searches):
            menu.Append(1+idx, txt)
        return menu
    
