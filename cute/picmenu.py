import os.path
import wx

class PicMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)
        
        self.parent = parent        
        self.bmpdir = self.parent.rundir + '/bitmaps/16/'
        
    def Append(self, id, label, picname=None):        
        item = wx.MenuItem(self, id, label) 
        if picname:       
            bitmap = self.bmpdir + picname
            if os.path.exists(bitmap):
                item.SetBitmap(wx.BitmapFromImage(wx.Image(bitmap, wx.BITMAP_TYPE_PNG)))
            
        return self.AppendItem(item)