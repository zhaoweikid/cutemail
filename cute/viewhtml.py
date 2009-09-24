import string, sys, os
import wx
import wx.html
import  wx.lib.mixins.listctrl  as  listmix
import mailparse, imagelist, logfile
from logfile import loginfo, logwarn, logerr

if sys.platform.startswith('win'):
    class AttachListCtrl (imagelist.ImageListWin):
        def __init__(self, parent, rundir, size=wx.Size(48,100)):
            imagelist.ImageListWin.__init__(self, parent, rundir)
else:
    class AttachListCtrl (imagelist.ImageListUnix):
        def __init__(self, parent, rundir, size=wx.Size(48,100)):
            imagelist.ImageListUnix.__init__(self, parent, rundir)

        
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
elif wx.Platform == '__WXMAC__':
    import wx.webkit
    class ViewHtml (wx.Panel):
        def __init__(self, parent):
            wx.Panel.__init__(self, parent, -1)
            
            self.html = wx.webkit.WebKitCtrl(self, -1)
            self.box = wx.BoxSizer(wx.VERTICAL)
            self.box.Add(self.html, 1, wx.GROW)
             
            self.SetSizer(self.box)
    
        def set_text(self, text):
            self.html.SetPageSource(text)
            
        def set_url(self, url):
            self.html.LoadURL(url)
 
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
            
            
            
            
