#!/usr/bin/python
#-*- encoding: utf-8 -*-
import sys, os
import wx
sys.path.append(os.getcwd() + os.sep + 'base')
sys.path.append(os.getcwd() + os.sep + 'mab')
from mab import mabwindow
import config, threadlist

class mabApp(wx.App):
    def __init__(self):                
        wx.App.__init__(self, 0)
        return None

    def OnInit(self):
        wx.InitAllImageHandlers()       
        self.frame = mabwindow.MainFrame(None, 101, config.VERSION)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)
        return True
        
    def OnActivate(self, event):
        if event.GetActive():
            #self.frame.OnActivate()
            pass
        event.Skip()
        

if __name__ == '__main__':
    thsch = threadlist.Schedule()
    thtask = threadlist.Task()
    thsch.start()
    thtask.start()
    
    app = mabApp()
    app.MainLoop()
    
    thsch.is_running = False
    thtask.is_running = False
    
    thsch.join()
    thtask.join()
    
    
