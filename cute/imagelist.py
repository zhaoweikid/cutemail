# coding: utf-8
import os, sys
import threading
import wx
from common import load_bitmap, load_image
import mailparse, logfile
from logfile import loginfo, logwarn, logerr

#class ImageList (wx.Frame):
class ImageList (wx.Panel):
    def add_file(self, filename, data=None):
        pass

    def remove_file(self, filename):
        pass

    def clear(self):
        pass



class ImageListWin (wx.Panel):
    def __init__(self, parent, rundir, size=wx.Size(-1,-1)):
        wx.Panel.__init__(self, parent, -1)
        #wx.Frame.__init__(self, None, -1, size=(800, 600))
        self.SetBackgroundColour(wx.Colour(255,0,0))
        self.list = wx.ListCtrl(self, -1, style=wx.LC_ICON|wx.LC_AUTOARRANGE)
        self.data = []
        self.lastitem = None
        
        self.extensions = [".gif", '.png', '.jpg', '.jpeg', '.bmp', '.exe', '.zip', '.rar', '.doc', 
                        '.xls', '.ppt', '.txt', '.pdf', '.eml', '.chm', '.mdb', '.dll', '.ini', '.bat', 
                        '.htm', '.html']
        self.rundir = rundir
        self.extmap = {}

        self.il = wx.ImageList(32, 32, True)
        
        for name in self.extensions:
            x = self.load_win_icon(name)
            if x:
                ilmax = self.il.Add(x)
                self.extmap[name] = ilmax
        
        x = self.load_win_shell32_icon(2)
        ilmax = self.il.Add(x)
        self.extmap['.exe'] = ilmax

        self.list.AssignImageList(self.il, wx.IMAGE_LIST_NORMAL)

        #for x in range(0, ilmax+1):
        #    self.list.InsertImageStringItem(x, '%d'% (x), x)
        
        sizer = wx.BoxSizer()
        sizer.Add(self.list, flag=wx.ALL|wx.EXPAND, border=0, proportion=1)
        
        self.SetSizer(sizer)
        
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
        self.list.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

    def add_file(self, filename, data=None):
        s = os.path.splitext(filename)
        extname = s[1]
        #print 'extname:', extname
        if not self.extmap.has_key(extname):
            x = self.load_win_icon(extname)  
            if x:
                idx = self.il.Add(x)
                self.extmap[extname] = idx
            else:
                extname = '.exe'

        i = self.extmap[extname]
        itemidx = self.list.InsertImageStringItem(i, filename, i)
        if data:
            idx = len(self.data)
            self.data.append(data)
            self.list.SetItemData(itemidx, idx)

    def remove_file(self, filename):
        item = self.list.FindItem(-1, filename)
        if not item:
            logerr('not found:', filename)
            return

        data = self.list.GetItemData(item)
        if data:
            self.data.remove(data)
        self.list.DeleteItem(item)
    
    def remove_item(self, item=None):
        if not item and self.lastitem == None:
            return

        item = self.lastitem
        data = self.list.GetItemData(item)
        if data:
            self.data.remove(data)
        self.list.DeleteItem(item)

    def clear(self):
        self.data = []
        self.list.ClearAll()

    def load_win_shell32_icon(self, idx):
        tmpicon = wx.Icon("c:\windows\system32\shell32.dll;%s" %(idx), wx.BITMAP_TYPE_ICO)
        bmp = wx.BitmapFromIcon(tmpicon)
        return bmp 

    def load_win_icon(self, extname):
        import _winreg

        root = _winreg.ConnectRegistry(None, _winreg.HKEY_CLASSES_ROOT)
        try:
            key = _winreg.OpenKey(root, extname)  
        except:
            return None
        value = _winreg.QueryValue(key, '')
        newkey = value+r'\DefaultIcon'
        try:
            key = _winreg.OpenKey(root, newkey)
        except:
            newkey2 = value + r'\CurVer' 
            try:
                key = _winreg.OpenKey(root, newkey2)
            except:
                return None
            value = _winreg.QueryValue(key, '')
            
            newkey3 = value + r'\DefaultIcon'
            try:
                key = _winreg.OpenKey(root, newkey3)
            except:
                return None

        value = _winreg.EnumValue(key, 0)
        result = value[1]
        #print 'result:', result
        if result.find('%SystemRoot%') >= 0:
            result = result.replace('%SystemRoot%', os.environ['SystemRoot'])
        if result[0] == '%':
            return None
        result = result.replace(',', ';')
        tmpicon = wx.Icon(result, wx.BITMAP_TYPE_ICO)
        bmp = wx.BitmapFromIcon(tmpicon)
        
        return bmp
    
    def OnItemActivated(self, event):
        itemidx = event.m_itemIndex
        dataidx = self.list.GetItemData(itemidx)
        loginfo('dataidx:', dataidx)
        if dataidx < 0:
            loginfo('not found dataidx.')
            return
        data = self.data[dataidx]
        if not data.has_key('home'):
            loginfo('not found home in data')
            return

        tmpdir = os.path.join(data['home'], 'tmp')
        loginfo('file:', data['file'], ' attach:', data['attach'])
        tmpdir = os.path.join(data['home'], 'tmp')
        mailparse.decode_attach(data['file'], data['attach'], tmpdir)
        
        attachfile = os.path.join(tmpdir, data['attach'])
        if os.path.isfile(attachfile):
            #wx.Execute(attachfile)
            loginfo('execute:', attachfile)
            self.Execute(attachfile)
        
    def Execute(self, cmd):
        import subprocess
        subprocess.Popen(cmd.encode('gbk'), shell=True)
    
    def OnItemSelected(self, event):
        self.lastitem = event.m_itemIndex
        loginfo('imagelist last item:', self.lastitem)


    def OnKeyUp(self, evt):
        loginfo('key up:', evt.GetKeyCode())
        if 127 == evt.GetKeyCode():
            self.remove_item()                

class ImageListUnix (wx.Panel):
    def __init__(self, parent, rundir, size=wx.Size(48,48)):
        wx.Panel.__init__(self, parent, -1)
        #wx.Frame.__init__(self, None, -1, size=(800, 600))
        self.SetBackgroundColour(wx.Colour(255,0,0))
        self.list = wx.ListCtrl(self, -1, style=wx.LC_ICON|wx.LC_AUTOARRANGE)
        self.data = []
        self.lastitem = None
        
        self.extensions = [".gif", '.png', '.jpg', '.jpeg', '.bmp', '.exe', '.zip', '.rar', '.doc', 
                        '.xls', '.ppt', '.txt', '.pdf', '.eml', '.chm', '.mdb', '.dll', '.ini', '.bat', 
                        '.htm', '.html']
        self.rundir = rundir
        self.extmap = {}

        self.il = wx.ImageList(32, 32, True)
        
        for name in self.extensions:
            x = self.load_unix_icon(name)
            if x:
                ilmax = self.il.Add(x)
                self.extmap[name] = ilmax
        
        self.list.AssignImageList(self.il, wx.IMAGE_LIST_NORMAL)

        #for x in range(0, ilmax+1): #    self.list.InsertImageStringItem(x, '%d'% (x), x) 
        sizer = wx.BoxSizer()
        sizer.Add(self.list, flag=wx.ALL|wx.EXPAND, border=0, proportion=1)
        
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
        self.list.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

    def add_file(self, filename, data=None):
        s = os.path.splitext(filename)
        extname = s[1]
        #print 'extname:', extname
        if not self.extmap.has_key(extname):
            x = self.load_unix_icon(extname)  
            if x:
                idx = self.il.Add(x)
                self.extmap[extname] = idx
            else:
                extname = '.exe'

        i = self.extmap[extname]
        itemidx = self.list.InsertImageStringItem(i, filename, i)
        if data:
            idx = len(self.data)
            self.data.append(data)
            self.list.SetItemData(itemidx, idx)

    def remove_file(self, filename):
        item = self.list.FindItem(-1, filename)
        if not item:
            logerr('not found:', filename)
            return

        data = self.list.GetItemData(item)
        if data:
            self.data.remove(data)
        self.list.DeleteItem(item)
    
    def remove_item(self, item=None):
        if not item and self.lastitem == None:
            return

        item = self.lastitem
        data = self.list.GetItemData(item)
        if data:
            self.data.remove(data)
        self.list.DeleteItem(item)

    def clear(self):
        self.data = []
        self.list.ClearAll()
    
    def load_unix_icon(self, extname):
        return load_bitmap(os.path.join(self.rundir, 'bitmaps', '32', 'www.png'))
    
    def OnItemActivated(self, event):
        itemidx = event.m_itemIndex
        dataidx = self.list.GetItemData(itemidx)
        if not dataidx:
            return
        data = self.data[dataidx]
        if not data.has_key('home'):
            return

        tmpdir = os.path.join(data['home'], 'tmp')
        loginfo('file:', data['file'])
        tmpdir = os.path.join(data['home'], 'tmp')
        mailparse.decode_attach(data['file'], data['attach'], tmpdir)
        
        attachfile = os.path.join(tmpdir, data['attach'])
        if os.path.isfile(attachfile):
            #wx.Execute(attachfile)
            loginfo('execute:', attachfile)
            self.Execute(attachfile)
        
    def Execute(self, cmd):
        import subprocess
        subprocess.Popen(cmd.encode(mailparse.charset), shell=True)
    
    def OnItemSelected(self, event):
        self.lastitem = event.m_itemIndex
        loginfo('imagelist last item:', self.lastitem)

    def OnKeyUp(self, evt):
        loginfo('key up:', evt.GetKeyCode())
        if 127 == evt.GetKeyCode():
            self.remove_item()                



def imagelist_class():
    if sys.platform.startswith('win'):
        return ImageListWin
    else:
        return ImageListUnix


class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, size=(800, 600))

        sizer = wx.BoxSizer(wx.VERTICAL)
        panel = imagelist_class()(self, rundir=os.path.dirname(os.getcwd()))
        sizer.Add(panel, 0, wx.ALL|wx.EXPAND, border=1)
        
        panel.add_file("file.exe")
        panel.add_file("file1.png")
        panel.add_file("file.pdf")
        panel.add_file("file.htm")
        panel.add_file("file.xxx")

        self.SetSizer(sizer)
        self.SetAutoLayout(True)


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = TestFrame()
    frame.Show()
    app.MainLoop()

            
