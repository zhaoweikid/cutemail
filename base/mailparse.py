#!-*- encoding:gbk -*-
import os, sys, time, string, shutil, types
import email
from email.Charset       import Charset
from email.Header        import Header, decode_header, make_header
from email.Parser        import Parser, HeaderParser
from email.Generator     import Generator, DecodedGenerator
from email.Message       import Message
from email.MIMEAudio     import MIMEAudio
from email.MIMEText      import MIMEText
from email.MIMEImage     import MIMEImage
from email.MIMEBase      import MIMEBase
from email.MIMEMessage   import MIMEMessage
from email.MIMEMultipart import MIMEMultipart
import locale

charset = locale.getdefaultlocale()[1]

def decode_string(s):
    h = Header(s, errors='ignore')
    dh = decode_header(h)
    return dh[0][0];
 
def get_content(msg, ret):    
    if msg.is_multipart():
        ilen = len(msg.get_payload())
        for i in range(0, ilen):
            subpart = msg.get_payload(i)
            get_content(subpart, ret)
    else:
        if not msg.get_param("name"):
            subtype = msg.get_content_subtype()
            #print msg.get("content-type")
            #print subtype
            chars = msg.get_content_charset().strip().lower()
            if chars:
                if chars == 'gb2312':
                    chars = 'gbk'
                ret['charset'] = chars

            cnt = msg.get_payload(decode=True)
            if subtype == 'plain':
                ret['plain'] = cnt
            elif subtype == 'html':
                ret['html'] = cnt
        else:
            cid = msg.get('content-id')
            if cid:
                cid = cid.strip('<')
                cid = cid.strip('>')
            else:
                cid = ''
            print 'content-id:', cid
            aname = decode_string(msg.get_param('name'))
            ret['attach'].append([aname, cid])

def decode_mail_file(mailfile):
    #ret = {'file':mailfile, 'from':'', 'to':'', 'subject':'', 'size':0, 'date':'', 'plain':'', 'html':'', 'charset':'gbk', 'attach':[]}
    ret = {'id':'','name':'','filename':'','plain':'','html':'','header':'','subject':'',
           'mailfrom':'','mailto':[],'mailcc':[],'size':0,'ctime':0,
           'mailbox':'','status':'','position':0,'thread':''}
    
    ret['size'] = os.path.getsize(mailfile)
    fp = open(mailfile, "r")
    msg = email.message_from_file(fp)
    
    print msg.get("subject")    
    ret['subject'] = decode_string(msg.get("subject"))
    ret['mailfrom'] = email.utils.parseaddr(msg.get("from"))[1]
    ret['mailto']   = email.utils.parseaddr(msg.get("to"))[1]
    ret['mailcc']   = email.utils.parseaddr(msg.get("cc"))[1]
    ret['date'] = msg.get('date')
    ret['ctime'] = time.time()

    text = get_content(msg, ret)
    fp.close() 

    return ret
 
def decode_mail_string(maildata):
    #ret = {'file':mailfile, 'from':'', 'to':'', 'subject':'', 'size':0, 'date':'', 'plain':'', 'html':'', 'charset':'gbk', 'attach':[]}
    ret = {'filename':'','plain':'','html':'','header':'','subject':'',
           'mailfrom':'','mailto':[],'mailcc':[],'size':0,'ctime':0,'date':'',
           'attach':[],'mailbox':'','status':'new','thread':'', 'charset':''}
    
    ret['size'] = len(maildata)
    msg = email.message_from_string(maildata)
    
    ret['subject'] = decode_string(msg.get("subject"))
    ret['mailfrom'] = email.utils.parseaddr(msg.get("from"))[1]
    ret['mailto']   = email.utils.parseaddr(msg.get("to"))[1]
    ret['mailcc']   = email.utils.parseaddr(msg.get("cc"))[1]
    ret['date'] = msg.get('date')
    ret['ctime'] = time.time()

    text = get_content(msg, ret)
    
    if ret['charset']:
        ret['subject'] = unicode(ret['subject'], ret['charset'], 'ignore')

    return ret
 
def get_attach(msg, dirname, filename):    
    if msg.is_multipart():
        ilen = len(msg.get_payload())
        for i in range(0, ilen):
            subpart = msg.get_payload(i)
            get_attach(subpart, dirname, filename)
    else:
        if msg.get_param("name"):
            aname = decode_string(msg.get_param('name'))
            if type(filename) == types.ListType:
                if aname in filename:
                    f = open(dirname + os.sep + aname, "wb")
                    cnt = msg.get_payload(decode=True)
                    f.write(cnt)
                    f.close()
            else:
                if aname == filename:
                    f = open(dirname + os.sep + filename, "wb")
                    cnt = msg.get_payload(decode=True)
                    f.write(cnt)
                    f.close()

 
def decode_attach(mailfile, filename, tmpdir='tmp'):
    if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir)
    if type(filename) == types.UnicodeType:
        filename = filename.encode(charset)
    if type(mailfile) == types.UnicodeType:
        mailfile = mailfile.encode(charset)
    #fpath = tmpdir + os.sep + mailfile
    fp = open(mailfile, "r")
    msg = email.message_from_file(fp)
    get_attach(msg, tmpdir, filename)  
    fp.close() 


def decode_attachs(mailfile, filenames, tmpdir='tmp'):
    if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir)

    for i in xrange(0, len(filenames)):
        filename = filenames[i]
        if type(filename) == types.UnicodeType:
            filename[i] = filename.encode(charset)
    if type(mailfile) == types.UnicodeType:
        mailfile = mailfile.encode(charset)
    #fpath = tmpdir + os.sep + mailfile
    fp = open(mailfile, "r")
    msg = email.message_from_file(fp)
    get_attach(msg, tmpdir, filenames)  
    fp.close() 



def main(dirname):
    if os.path.isdir(dirname):
        ld = os.listdir(dirname)
        for x in ld:
            ret = decode_mail(x) 
            print ret
    elif os.path.isfile(dirname):
        ret = decode_mail_file(dirname)
        print ret

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'usage: decodemail.py filename [attachname]'
        sys.exit()

    if len(sys.argv) == 2:
        main(sys.argv[1])  
    elif len(sys.argv) == 3:
        decode_attach(sys.argv[1], sys.argv[2])
    
       

