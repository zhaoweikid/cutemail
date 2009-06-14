import os, string
import sys, smtplib, base64
from sender.mxrecord import MXRecord
import re

IP_ADDR = re.compile("[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")

class Sender:
    def __init__(self, smtpserver, smtpport=25, helo=1, username=None, passwd=None):
        self.helo = helo
        if helo != 1: # ready to say ehlo
            self.username = username
            self.passwd = passwd
            self.server = smtpserfver
            self.port = smtpport
            self.mx = None
        else:
            if IP_ADDR.match(smtpserver):                
                self.server = smtpserfver
            else:
                self.mx = MXRecod(smtpserver)
                self.server = self.mx.get_mx_min()
            self.port = smtpport
            self.username = None
            self.passwd = None
            
    
    def connect(self):
        self.svr = smtplib.SMTP(self.server, self.port)
        self.svr.set_debuglever(1)
        if self.helo == 1:
            self._say_helo("ms")
        else:
            self._say_ehlo("ms")
        
    def _say_helo(self, domain):
        self.svr.docmd("HELO "+domain)
    
    def _say_ehlo(self, domain, username, passwd):
        self.svr.docmd("EHLO "+domain)
        self.svr.docmd("AUTH LOGIN")
        self.svr.docmd(base64.encodestring(self.username))
        # if smtpserver is 163.com maybe do getreply() at this point
        self.svr.docmd(base64.encodestring(self.passwd))
        
        
    def sendstring(self, data, touser, username, passwd):
        if not data:
            return -1
        self.svr.docmd("MAIL FROM: %s" % (username))
        self.svr.docmd("RCPT TO: %s" %(touser))
        self.svr.docmd("DATA")
        self.svr.send(data)
        self.svr.send("\r\n.\r\n")
        self.svr.getreply()
    
    def quit(self):
        self.svr.quit()
        
        
        