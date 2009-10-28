#!/usr/bin/env python
# coding: utf-8
import base64
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Utils, Encoders
import mimetypes, sys, email, os
import string, time, types
import logfile
from logfile import loginfo, logwarn, logerr

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
            v = self.headdict[k]
            newk = '-'.join(map(string.capitalize, k.lower().split('-')))

            if newk == 'Subject':
                self.msg[newk] = email.Header.Header(v, "UTF-8")
            elif newk == 'From':
                if type(v) == types.ListType:
                    self.msg[newk] = '"%s" <%s>' % (email.Header.Header(v[0], 'utf-8'), v[1])
                else:
                    self.msg[newk] = v
            elif newk == 'To':
                s = []
                for x in v:
                    if type(x) == types.ListType:
                        s.append('"%s" <%s>' % (email.Header.Header(x[0], 'utf-8'), x[1]))
                    else:
                        s.append(x)
                self.msg[newk] = '\r\n\t'.join(s)
            else:
                self.msg[newk] = v

        self.msg['Date'] = Utils.formatdate(localtime = 1)
        self.msg['Message-Id'] = Utils.make_msgid()

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
            onlyfilename = os.path.basename(filename)
            loginfo('type:', type(onlyfilename))
            onlyfilename = '=?utf-8?b?%s?=' % (base64.b64encode(onlyfilename.encode('utf-8')))
            loginfo('onlyfilename:', onlyfilename)
            attachment = MIMEText(Encoders._bencode(open(filename, 'rb').read()))
            attachment.replace_header('Content-type', 'Application/octet-stream: name="' + onlyfilename + '"')
            attachment.replace_header('Content-Transfer-Encoding', 'base64')
            attachment.add_header('Content-Disposition', 'attachment;filename="' + onlyfilename + '"')
            self.attach.attach(attachment)

    def generate_email(self):
        self.generate_head()
        self.generate_body()
        self.mail = self.msg.as_string().strip()+'\n' + self.attach.as_string()
        return self.mail
       
if __name__ == '__main__':
    headdic = {'from': 'lanwenhong@eyou.net', 'to': ['rubbish_lan@sohu.com'], 'subject': 'this is test email'}
    msg_text = 'plain text infomation'
    msg_html = '<font color="read">html text infomation</font>'
    filelist = []
    filelist.append('/home/lanwenhong/project/1234447255.mp3')

    createemail = CreateEmail(msg_text, msg_html, filelist, headdic)
    email = createemail.generate_email()
    print email

