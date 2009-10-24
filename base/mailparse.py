# coding: utf-8
import os, sys, time, string, shutil, types
import time, datetime
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
import locale, traceback
import logfile
from logfile import loginfo, logwarn, logerr

charset = locale.getdefaultlocale()[1]

month = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 
         'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}

def parsedate(s):
    if not s:
        return '%d-%02d-%02d %02d:%02d:%02d' % time.localtime()[:6]
    s = s.strip()
    pos = s.find(',')
    if pos > 0:
        s = s[pos+1:].strip()
    ns = s.split()
    try:
        if len(ns) < 4:
            if ns[0].count('-') == 2:
                ts = ns[0].split('-')
                return '%s-%02d-%02d %s'% (ts[0], int(ts[1]), int(ts[2]), ns[1])
            return '%d-%02d-%02d %02d:%02d:%02d' % time.localtime()[:6]
        if ns[3].count(':') == 1:
            ns[3] = ns[3] + ':00'
        return '%s-%02d-%s %s' % (ns[2], month[ns[1]], ns[0], ns[3])
    except ValueError, e:
        logwarn('date string:', s)
        logerr(traceback.format_exc())
    return '%d-%02d-%02d %02d:%02d:%02d' % time.localtime()[:6]


def decode_string(s, defcharset='gbk'):
    h = Header(s, errors='ignore')
    dh = decode_header(h)
    charset = dh[0][1]
    s = dh[0][0]
    if charset:
        s = unicode(s, charset, 'ignore')
    else:
        iscn = False
        for i in xrange(0, len(s)):
            if ord(s[i]) > 127:
                iscn = True
                break
        if iscn:
            s = unicode(s, defcharset, 'ignore')
    return s
 
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
            chars = msg.get_content_charset()
            if chars:
                chars = chars.strip().lower()
                if chars == 'gb2312':
                    chars = 'gbk'
                ret['charset'] = chars

            cnt = msg.get_payload(decode=True)
            try:
                cnt = unicode(cnt, ret['charset'], 'ignore')
            except Exception, e:
                logerr('charset convert error:', e)
 
            if subtype == 'plain':
                ret['plain'] = ret['plain'] + '\r\n' + cnt
            elif subtype == 'html':
                ret['html'] = cnt
        else:
            cid = msg.get('content-id')
            if cid:
                cid = cid.strip('<')
                cid = cid.strip('>')
            else:
                cid = ''
            #print 'content-id:', cid
            aname = decode_string(msg.get_param('name'))
            ret['attach'].append([aname, cid])


def decode_message(msg, ret):
    ret['subject'] = decode_string(msg.get("subject"))
    ret['from'] = list(email.utils.parseaddr(msg.get("from")))
    ret['from'][0] = decode_string(ret['from'][0])
    ret['to'].append(email.utils.parseaddr(msg.get("to")))
    ret['date'] = parsedate(msg.get('date'))

    text = get_content(msg, ret)

    '''
    oldstr = ret['subject']
    if oldstr:
        iscn = False
        for x in oldstr: 
            if ord(x) > 127:
                iscn = True 
        if iscn:
            ret['subject'] = unicode(oldstr, ret['charset'])
    else:
        ret['subject'] = u'无主题'
    '''


def decode_mail(mailfile):
    ret = {'file':mailfile, 'from':None, 'to':[], 'subject':'', 'size':0, 'date':'', 'plain':'', 'html':'', 'charset':'gbk', 'attach':[]}
    
    ret['size'] = os.path.getsize(mailfile)
    fp = open(mailfile, "r")
    msg = email.message_from_file(fp)
    
    decode_message(msg, ret)

    fp.close() 
    return ret


def decode_mail_string(mailstr):
    ret = {'file':'', 'from':None, 'to':[], 'subject':'', 'size':0, 'date':'', 'plain':'', 'html':'', 'charset':'gbk', 'attach':[]}
    
    ret['size'] = len(mailstr)
    msg = email.message_from_string(mailstr)
    
    decode_message(msg, ret)

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
                loginfo('aname:', type(aname), aname)
                loginfo('filename:', type(filename), filename)
                if aname == filename:
                    tmpfile = os.path.join(dirname, filename)
                    loginfo('tmpfile:', tmpfile)
                    f = open(tmpfile, "wb")
                    cnt = msg.get_payload(decode=True)
                    loginfo('write:', len(cnt))
                    f.write(cnt)
                    f.close()

 
def decode_attach(mailfile, filename, tmpdir='tmp'):
    if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir)
    #if type(filename) == types.UnicodeType:
    #    filename = filename.encode(charset)
    #if type(mailfile) == types.UnicodeType:
    #    mailfile = mailfile.encode(charset)
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
        ret = decode_mail(dirname)
        print ret

def test1():
    if len(sys.argv) < 2:
        print 'usage: decodemail.py filename [attachname]'
        sys.exit()

    if len(sys.argv) == 2:
        main(sys.argv[1])  
    elif len(sys.argv) == 3:
        decode_attach(sys.argv[1], sys.argv[2])
    
def test2():
    print parsedate(sys.argv[1]) 


if __name__ == '__main__':
    test2()


