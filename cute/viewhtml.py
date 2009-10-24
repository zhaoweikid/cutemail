import string, sys, os
import wx
import wx.html
import wx.lib.mixins.listctrl  as  listmix
import mailparse, imagelist, logfile
from logfile import loginfo, logwarn, logerr


def html2text(text):
    import re
    rex  = re.compile("<br[/ ]*>", re.IGNORECASE) 
    text = re.sub(rex, '\n', text)
    rex  = re.compile("<[/!]?[a-zA-Z]+[^>]*>", re.DOTALL)
    text = re.sub(rex, '', text)
    rex  = re.compile("<!--.*-->", re.DOTALL)
    text = re.sub(rex, '', text)
    rex  = re.compile("<(script|style).*</(script|style)[^>]*>", re.IGNORECASE|re.DOTALL)
    text = re.sub(rex, '', text)
    
    return text

 
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

        def set_text_auto(self, html, text):
            if html:
                self.set_text(html)
            else:
                self.set_text(text.replace('\r\n', '<br>').replace('\n', '<br>'))

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

        def set_text_auto(self, html, text):
            if html:
                self.set_text(html)
            else:
                self.set_text(text.replace('\r\n', '<br>').replace('\n', '<br>'))

 
else:
    class ViewHtml (wx.Panel):
        def __init__(self, parent):
            wx.Panel.__init__(self, parent, -1)
            
            #self.html = wx.html.HtmlWindow(self, -1)
            self.html = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
            self.box = wx.BoxSizer(wx.VERTICAL)
            self.box.Add(self.html, 1, wx.GROW)
             
            self.SetSizer(self.box)
    
        def set_text(self, text):
            #self.html.SetPage(text)
            self.html.SetValue(text)
            
        def set_url(self, url):
            #self.html.LoadPage(url)
            self.html.SetValue(url)
            
        def set_text_auto(self, html, text):
            if text:
                self.set_text(text)
            else:
                self.set_text(html2text(text))


           
