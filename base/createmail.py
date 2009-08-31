#!/usr/bin/env python
#-*- encoding: UTF-8 -*-

from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Utils, Encoders
import mimetypes, sys, email, os
import string, time

class CreateEmail:
    def __init__(self, messagetext, messagehtml, filelist, headdict):
        self.messagetext = messagetext
        self.messagehtml = messagehtml
        self.filelist = filelist
        self.headdict = headdict
        self.msg = email.Message.Message()
        self.attach = MIMEMultipart() 
        self.mail = ""

    def generate_head(self):
        for k in self.headdict.keys():
            if k == 'subject' or k == 'from' or k == 'to':
                self.msg[k] = email.Header.Header(self.headdict[k], "UTF-8")
            else:
                self.msg[k] = self.headdict[k]

        self.msg['date'] = Utils.formatdate(localtime = 1)
        self.msg['message-id'] = Utils.make_msgid()

    def generate_body(self):
        #创建纯文本
        if self.messagetext:
            body_plain = MIMEText(self.messagetext, _subtype = 'plain', _charset = 'UTF-8')
            if body_plain:
                self.attach.attach(body_plain)
        #创建超文本
        if self.messagehtml:
            body_html = MIMEText(self.messagehtml, _subtype = 'html', _charset = 'UTF-8')
            if body_html:
                self.attach.attach(body_html)
      
            
        #创建附件
        for filename in self.filelist:
            attachment = MIMEText(Encoders._bencode(open(filename, 'rb').read()))
            attachment.replace_header('Content-type', 'Application/octet-stream: name="' + os.path.basename(filename) + '"')
            attachment.replace_header('Content-Transfer-Encoding', 'base64')
            attachment.add_header('Content-diposition', 'attachment;filename="' + os.path.basename(filename) + '"')
            self.attach.attach(attachment)

    def generate_email(self):
        self.generate_head()
        self.generate_body()
        self.mail = self.msg.as_string().strip()+'\n' + self.attach.as_string()
        return self.mail
       
if __name__ == '__main__':
    headdic = {'from': 'lanwenhong@eyou.net', 'to': 'rubbish_lan@sohu.com', 'subject': 'this is test email'}
    msg_text = 'plain text infomation'
    msg_html = '<font color="read">html text infomation</font>'
    filelist = []
    filelist.append('/home/lanwenhong/project/1234447255.mp3')

    createemail = CreateEmail(msg_text, msg_html, filelist, headdic)
    email = createemail.generate_email()
    print email

