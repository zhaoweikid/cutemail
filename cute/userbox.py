# coding: utf-8
import os, sys
import wx


class UserBoxInfo(wx.Panel):
    def __init__(self, parent, path):
        wx.Panel.__init__(self, parent)
        self.user = path[1:]
        
        self.SetBackgroundColour((255,255,255))

