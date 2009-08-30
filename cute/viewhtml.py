import string, sys, os
import wx
import wx.html
import  wx.lib.mixins.listctrl  as  listmix
import mailparse, imagelist

class AttachListCtrl (imagelist.ImageList):
    def __init__(self, parent, rundir, size=wx.Size(-1,-1)):
        imagelist.ImageList.__init__(self, parent, rundir)
        
if wx.Platform == '__WXMSW__':
    import wx.lib.iewin as iewin

    class ViewHtml (wx.Panel):
        def __init__(self, parent):
            wx.Panel.__init__(self, parent, -1)
        
            self.html = iewin.IEHtmlWindow(self)
            self.box = wx.BoxSizer(wx.HORIZONTAL)
            self.box.Add(self.html, 1, wx.GROW)
         
            self.SetSizer(self.box)

        def set_text(self, text):
            self.html.LoadString(text)
            
        def set_url(self, url):
            self.html.Navigate(url)

else:
    class ViewHtml (wx.Panel):
        def __init__(self, parent):
            wx.Panel.__init__(self, parent, -1)
            
            self.html = wx.html.HtmlWindow(self, -1)
            self.box = wx.BoxSizer(wx.VERTICAL)
            self.box.Add(self.html, 1, wx.GROW)
             
            self.SetSizer(self.box)
    
        def set_text(self, text):
            self.html.SetPage(text)
            
        def set_url(self, url):
            self.html.LoadPage(url)
            
            
            
            