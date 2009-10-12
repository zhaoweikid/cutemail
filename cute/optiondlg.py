# coding: utf-8
import os, sys
import wx
import wx.lib.sized_controls as sc
import config, logfile
from logfile import loginfo, logwarn, logerr

class OptionsDialog(sc.SizedDialog):
    def __init__(self, parent, usercf):
        sc.SizedDialog.__init__(self, None, -1, u"账户属性", 
                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent

        keys = ['name','mailname','email','recv_interval','reserve_time',
            'pop3_server','pop3_pass','smtp_server','smtp_pass'] 
        vals = []
        for k in keys:
            loginfo('find:', k)
            i = config.cf.mailuser_fields.index(k)
            vals.append(config.cf.mailuser_fields_cn[i])
       
        pane = self.GetContentsPane()
        pane.SetSizerType("form")
        

        self.items = {}
        for i in range(0, len(keys)):
            loginfo('option:', keys[i], usercf[keys[i]])
            wx.StaticText(pane, -1, vals[i])
            if keys[i].endswith('pass'):
                x = wx.TextCtrl(pane, -1, usercf[keys[i]], size=(60, -1), style=wx.TE_PASSWORD)
            else:
                x = wx.TextCtrl(pane, -1, usercf[keys[i]], size=(60, -1))
            x.SetSizerProps(expand=True)
            self.items[keys[i]] = x

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        
        self.SetMinSize(wx.Size(400, 350))
        self.Fit()


    def get_values(self):
        data = {}

        for k in self.items:
            x = self.items[k]
            val = x.GetValue().strip() 
            data[k] = val
        return data


