# coding: utf-8
import string, os, sys, time, random
import traceback
import poplib, config, mailparse, utils
import logfile
from logfile import loginfo, logwarn, logerr

class POP3Client:
    def __init__(self, mailuser):
        self.username = mailuser['email']
        self.password = mailuser['pop3_pass']
        host = mailuser['pop3_server']
        self.hashdir_count = 10 
        self.uidl_pos = 0

        pos = string.find(host, ':')
        if pos > 0:
            self.server = host[:pos].strip()
            self.port = host[pos+1:].strip()
        else:
            self.server = host.strip()
            self.port = 110
        
        self.pop3 = poplib.POP3(self.server)
        self.pop3.set_debuglevel(0)
        
        # mailcount, mailsize
        self.info = [0, 0]
        self.uidls = []

        self.mailuser = mailuser
        self.home = config.cf.datadir+os.sep+mailuser['name']
        loginfo('home:', self.home)
        
        for n in config.cf.mailbox_map_cn2en.values():
            npath = self.home + os.sep + n
            if not os.path.isdir(npath):
                os.mkdir(npath)
        self.recvpath = self.home + os.sep + 'recv'

    def close(self):
        if self.pop3:
            self.pop3.quit()
            #self.pop3.sock.close()

    def init(self):
        lt = time.localtime()
        timedir = '%d%02d' % (lt[0], lt[1]) 
        #hashdir = str(int(time.time())%5)
        self.time_path = self.recvpath + os.sep + timedir
        #hash_path = time_path + os.sep + hashdir
        
        if not os.path.isdir(self.home):
            os.mkdir(self.home)
        if not os.path.isdir(self.time_path):
            os.mkdir(self.time_path)
        
        utils.maildir_init(self.time_path)

            
    def login(self):
        self.pop3.user(self.username)
        self.pop3.pass_(self.password)

    def infos(self):
        self.info = self.pop3.stat()
        s = self.pop3.uidl()
        info1 = s[1]
         
        for x in info1:
            x = string.strip(x)
            a = string.split(x)
            #loginfo('uidl:', a)
            if a[1] not in self.mailuser['uidls']:
                self.uidls.append(a)
        loginfo('uidl count:', len(self.uidls))

    def mails(self):
        name = self.mailuser['name']
        count = 0

        mailinfos = []
        for item in self.uidls:
            i, k = item
            loginfo('uidl:', i, k)
            trycount = 0
            while True:
                try:
                    data = self.pop3.retr(i)
                except Exception, e:
                    logerr(e)
                    trycount += 1
                    if trycount == 3:
                        break
                    continue
                trycount = 0
                break
            if trycount == 3:
                continue
            filedata = '\n'.join(data[1])
            
            hashdir = '%02d' % (hash(k) % self.hashdir_count)
            filename = os.path.join(self.time_path, hashdir, '%d.' % (int(time.time())) + k + '.eml')
            loginfo('file:', filename, 'size:', len(filedata))
            
            
            try:
                ret = mailparse.decode_mail_string(filedata)
            except Exception, e:
                traceback.print_exc(file=logfile.logobj.log)
                continue
            
            f = open(filename, 'w')
            f.write(filedata)
            f.close()
            
            ret['filename'] = filename[len(self.recvpath):]
            ret['mailbox'] = 'recv'
            ret['ctime'] = 'datetime()'
            ret['uidl'] = k
            mailinfos.append(ret)
            #print ret
            loginfo('======== count:', count, ' of ', len(self.uidls))
            #config.cf.mail_add(name, ret) 
        
            self.mailuser['uidls'].add(k)
            
            count += 1
        
        return mailinfos


    def mail(self):
        if self.uidl_pos >= len(self.uidls):
            return None

        name = self.mailuser['name']
        count = 0

        item = self.uidls[self.uidl_pos]
        self.uidl_pos += 1
            
        i, k = item
        loginfo('uidl:', i, k)
        trycount = 0
        while True:
            try:
                data = self.pop3.retr(i)
            except Exception, e:
                logerr(e)
                trycount += 1
                if trycount == 3:
                    raise ValueError, 'pop3 retr error:' + str(i)
                continue
            trycount = 0
            break
        filedata = '\n'.join(data[1])
          
        hashdir = '%02d' % (hash(k) % self.hashdir_count)
        filename = os.path.join(self.time_path, hashdir, '%d.' % (int(time.time())) + k + '.eml')
        loginfo('file:', filename, 'size:', len(filedata))
            
            
        try:
            ret = mailparse.decode_mail_string(filedata)
        except Exception, e:
            traceback.print_exc(file=logfile.logobj.log)
            raise
            
        f = open(filename, 'w')
        f.write(filedata)
        f.close()
            
        ret['filename'] = filename[len(self.recvpath):]
        ret['mailbox'] = 'recv'
        ret['ctime'] = int(time.time())
        ret['uidl'] = k
        ret['date'] = time.mktime(time.strptime(ret['date'], '%Y-%m-%d %H:%M:%S'))
        #print ret
        loginfo('======== pos:', self.uidl_pos, ' of ', len(self.uidls))
        #config.cf.mail_add(name, ret) 
        
        self.mailuser['uidls'].add(k)
        
        return ret

def test():
    for k in config.cf.users:
        print '---------- name:', k
        v = config.cf.users[k]
        p = POP3Client(v)
        p.init()
        p.login() 
        p.infos()
        p.mail()


if __name__ == '__main__':
    test()
    
