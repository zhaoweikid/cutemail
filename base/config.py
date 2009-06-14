#-*- encoding: utf-8 -*-
import os, string, sys, traceback, types
import dbtable, utils
import threading, Queue
import cPickle as pickle

VERSION = " MabMail 1.0"


# 全局配置信息
cf = None
# ui程序发送的任务队列
# {'name':'mailbox', 'task':'任务名'}
# 任务名包括: recvmail/sendmail
taskq = Queue.Queue()
# 发送给ui程序的消息队列
# {'name':'mailbox', 'task':'任务名', 'message':'参数 '}
# 任务名包括: updatebox/alert
uiq   = Queue.Queue()
    
class AppConfig:
    def __init__(self):            
        self.home = os.path.dirname(__file__)[:-5]
        # 用户配置
        self.users = {}
        # 以邮件地址为索引的用户信息
        self.mailboxs = {}
        
        self.mailbox_map = {u'收件箱':'recv', u'发件箱':'send', u'草稿箱':'draft',
                            u'已发送邮件':'sendover', u'垃圾邮件':'spam',
                            u'病毒邮件':'virus', u'删除邮件':'trash'}
        
        self.datadir = self.home + os.sep + 'data'
        if not os.path.isdir(self.datadir):
            os.mkdir(self.datadir)
        
        # status表示邮件状态可以为未读，已读，已回复
        self.mailinfo_fields = ['filename','plain','html','header','subject','mailfrom','mailto',
                          'mailcc','size','ctime','date','attach','mailbox','status','thread', 'charset']
        self.mailinfo_index  = ['mailbox', 'status']
        
        self.mailuser_fields = ['name','email','password','smtp','pop3','imap',
             'uidls','mailbox', 'schedule']
        
    def conf_init(self):
        #mbox = [unicode(u['name']), u'收件箱',u'发件箱', u'草稿箱', u'已发送邮件', u'垃圾邮件', u'病毒邮件', u'删除邮件']
        dx = ['','','','','','',set(),[],[]]
        x = dict(zip(self.mailuser_fields, dx))
        #x = {'name':'','email':'','password':'','smtp':'','pop3':'','imap':'',
        #     'uidl':set(),'mailbox':'', 'schedule': []}
        conf = {'config': x, 'mailinfo':None}
        
        return conf
    
    def user_add(self, incf):
        name = incf['name']
        email = incf['email']
        if self.users.has_key(name):
            raise ValueError, "user %s is exists" % (name)
        if self.mailboxs.has_key(email):
            raise ValueError, 'email %s is exists' % (email)
        
        conf = self.conf_init()
        conf['config'].update(incf)
        if not conf['config']['mailbox']:
            print 'add default mailbox'
            conf['config']['mailbox'] = [unicode(incf['name']), u'收件箱',u'发件箱', u'草稿箱', u'已发送邮件', u'垃圾邮件', u'病毒邮件', u'删除邮件']
            
        userpath = self.datadir + os.sep + name
        if not os.path.isdir(userpath):
            os.mkdir(userpath)
        infopath = userpath + os.sep + 'mailinfo'
        conf['mailinfo'] = dbtable.DBTable(infopath, self.mailinfo_fields)
        self.dump_conf(conf['config'])
        
        self.users[name] = conf
        self.mailboxs[email] = conf
     
    def user_delete(self, name):
        conf = self.users[name]
        email = conf['config']['email']
        self.dump_user(name)
        
        del self.users[name]
        del self.mailboxs[email]
        
        conf['mailinfo'].close()
        userdir = self.datadir + os.sep + name
        del conf
        os.rename(userdir, userdir+'.%d.bak' % (int(time.time())))

    
    def load(self):
        boxes = os.listdir(self.datadir)
        for box in boxes:
            if box.endswith(".bak"): # ignore dir name end with .bak
                continue
            conf_path = self.datadir + os.sep + box + os.sep + 'config.db'
            if not os.path.isfile(conf_path):
                continue
            
            if not os.path.isfile(conf_path):
                continue
            else:
                f = open(conf_path, 'r')
                conf = pickle.load(f)
                f.close()
                
            mailinfo_path   = self.datadir + os.sep + box + os.sep + "mailinfo"
            mailinfo   = dbtable.DBTable(mailinfo_path, self.mailinfo_fields, self.mailinfo_index)
            userconf = {'config': conf, 'mailinfo':mailinfo}
            self.users[conf['name']] = userconf
            self.mailboxs[conf['email']] = userconf
    
    def load_user(self, name):
        conf_path = self.datadir + os.sep + name + os.sep + 'config.db'
        f = open(conf_path, 'r')
        conf = pickle.load(f)
        f.close()
        return conf
                
            
    def dump_conf(self, cf):
        if type(cf) == types.StringType or type(cf) == types.UnicodeType:
            cf = self.users[cf]['config']
        confpath = self.datadir + os.sep + cf['name'] + os.sep + 'config.db'
        f = open(confpath, 'w')
        pickle.dump(cf, f)
        f.close()
    
    def dump_user(self, name):
        conf = self.users[name]
        self.dump_conf(conf['config'])
        conf['mailinfo'].sync()
        
    def dump(self):
        for u in self.users:
            self.dump_user(u)
          
    def mail_add(self, name, info):
        user = self.users[name]
        mailinfo = user['mailinfo']
        mailinfo.insert(info)
        mailinfo.sync() 
    
        
def load():
    global cf
    app = AppConfig()
    app.load()
    
    # for test
    u = {}
    u['name'] = 'test1'
    u['email'] = 'python25@163.com'
    u['password'] = '666666'
    u['pop3_server'] = 'pop3.163.com'
    u['mailbox'] = [unicode(u['name']), [u'收件箱', 'a', 'b', ['c', 'dd']],u'发件箱', u'草稿箱', u'已发送邮件', u'垃圾邮件', u'病毒邮件', u'删除邮件']
    
    try:  
        app.user_add(u)
    except Exception, e:
        traceback.print_exc()
        
    me = {'name':'zhaowei', 'email':'zhaowei@pythonid.com', 'password':'666666', 'pop3_server':'mail.pythonid.com'}
    try:  
        app.user_add(me)
    except Exception, e:
        traceback.print_exc()
    
    print 'users:', app.users        
    cf = app

load()

