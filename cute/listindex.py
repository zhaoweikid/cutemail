#!/usr/bin/python
import  wx
import  wx.html as  html
import  wx.lib.wxpTag

class ListIndex(html.HtmlWindow):
    def __init__(self, parent, id):
        html.HtmlWindow.__init__(self, parent, id, style=wx.NO_FULL_REPAINT_ON_RESIZE)