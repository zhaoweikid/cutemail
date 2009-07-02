import string, sys, os
import wx
import wx.html
import  wx.lib.mixins.listctrl  as  listmix

class AttachListCtrl (wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        
        self.imagelist = wx.ImageList(32, 32, True)
        self.image_default = self.imagelist.Add(wx.Bitmap("bitmaps/32/www.png", wx.BITMAP_TYPE_PNG))
        self.AssignImageList(self.imagelist, wx.IMAGE_LIST_NORMAL)
        
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        
    def OnDoubleClick(self, event):
        print 'double click'


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
            
            
            
            