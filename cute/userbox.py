# coding: utf-8
import os, sys, time
import wx
import wx.lib.sized_controls as sc
import config, dbope
from logfile import loginfo


class UserBoxInfo(sc.SizedPanel):
    def __init__(self, parent, path):
        sc.SizedPanel.__init__(self, parent)
        self.user = path[1:]
        
        self.SetBackgroundColour((255,255,255))
        self.SetSizerType("form")

        self.usercf = config.cf.users[self.user]
        
        wx.StaticText(self, -1, u'当前用户') 
        wx.StaticText(self, -1, self.user)
    
        self.display_sqls = []
        for x in self.usercf['mailbox'][1]:
            en = config.cf.mailbox_map_cn2en[x[0]]
            sql1 = "select count(*) from mailinfo where mailbox='%s'" % (en)
            sql2 = "select sum(size) from mailinfo where mailbox='%s'" % (en)
            
            wx.StaticText(self, -1, x[0]) 
            text = wx.TextCtrl(self, -1, '', size=(300,-1), style=wx.NO_BORDER|wx.TE_READONLY)

            self.display_sqls.append([en, sql1, sql2, text])

        self.display()
           

    def display(self):
        conn = dbope.openuser(config.cf, self.user)
        for x in self.display_sqls:
            mcount = conn.query(x[1], False)[0][0]
            msize  = conn.query(x[2], False)[0][0]
            if msize is None:
                msize = 0
            x[3].SetValue(u'信件%d封 大小%.2fM' % (mcount, float(msize)/1024/1024)) 
        conn.close()

        
        

        
