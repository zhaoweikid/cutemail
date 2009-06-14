import wx, cStringIO
import string, sys, os

def load_image(ipath):
    return wx.BitmapFromImage(wx.ImageFromStream(cStringIO.StringIO(open(ipath,'rb').read())))