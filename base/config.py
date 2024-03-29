#-*- encoding: utf-8 -*-
import os, string, sys, traceback, types
import mypprint
import utils
import threading, Queue
import cPickle as pickle
import dbope, logfile, linkman
from logfile import loginfo, logwarn, logerr
VERSION = " CuteMail 1.0"

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
        # 以用户为索引的用户配置
        self.users = {}
        # 以邮件地址为索引的用户配置信息
        self.mailboxs = {}
        self.linkman = None

        self.mailbox_cn_names = [u'收件箱', u'发件箱', u'草稿箱', u'已发送邮件', u'垃圾邮件', u'删除邮件']
        self.mailbox_en_names = ['recv', 'send', 'draft', 'sendover', 'spam', 'trash']
        
        self.mailbox_map_cn2en = {}
        for i in range(0, len(self.mailbox_cn_names)):
            self.mailbox_map_cn2en[self.mailbox_cn_names[i]] = self.mailbox_en_names[i]
            
        self.mailbox_map_en2cn = {}
        for i in range(0, len(self.mailbox_cn_names)):
            self.mailbox_map_en2cn[self.mailbox_en_names[i]] = self.mailbox_cn_names[i]
        
        self.datadir = os.path.join(self.home, 'data')
        if not os.path.isdir(self.datadir):
            os.mkdir(self.datadir)
        
        self.db = None
        # status表示邮件状态可以为未读(new)，已读(read)，已回复(reply)
        self.mailinfo_fields = ['filename','plain','html','header','subject','mailfrom','mailto',
                          'size','ctime','date','attach','mailbox','status','thread', 'charset']
        #self.mailinfo_index  = ['mailbox', 'status']
        
        # attach为用||分隔的多个文件名
        self.mailinfo_sql = '''create table if not exists mailinfo (
        id integer primary key autoincrement,
        filename varchar(255) not null,
        subject varchar(255),
        fromuser varchar(32),
        mailfrom varchar(128) not null,
        mailto varchar(128) not null,
        size integer default 0,
        ctime integer,
        date integer,
        attach text default '',
        mailbox varchar(64),
        tag varchar(32),
        status varchar(32) default 'new',
        threads integer default 0,
        uidl varchar(128),
        charset varchar(64) default 'gbk'
        )'''
        # 用户配置信息, recv_interval为接收间隔时间，单位为分，reserve_time为信件保留时间，
        # 单位为天，小于零表示不删除，等于0表示不保留， 大于零是保留天数
        self.mailuser_fields = ['name', 'storage', 'mailname', 'email',
            'reply_addr', 'recv_interval', 'reserve_time',
            'pop3_server','pop3_pass','smtp_server', 'smtp_pass',
            'uidls','mailbox', 'schedule']
        self.mailuser_fields_cn = [u'用户名', u'存储路径', u'姓名', u'邮件地址', u'回复地址',
                u'收信间隔时间(分)', u'信件在服务器上保留时间(天)', u'pop3服务器地址', u'pop3密码', 
                u'smtp服务器地址', u'smtp密码', u'邮件唯一标示', u'邮箱结构', u'定时任务']
        
    def conf_init(self):
        '''设置用户默认配置'''
        dx = [''] * len(self.mailuser_fields)
        x = dict(zip(self.mailuser_fields, dx))
        x['uidls'] = set()
        x['mailbox'] = []
        x['schedule'] = []
        return x 
    
    def user_add(self, incf):
        '''
        添加一个新用户
        incf - 该用户的配置信息。是以self.mailuser_fields为关键字申城的字典
        '''
        name = incf['name']
        email = incf['email']
        if self.users.has_key(name):
            raise ValueError, "user %s is exists" % (name)
        if self.mailboxs.has_key(email):
            raise ValueError, 'email %s is exists' % (email)
        
        conf = self.conf_init()
        conf.update(incf)
        if not conf['mailbox']:
            loginfo('add default mailbox')
            boxs = []
            for x in self.mailbox_cn_names:
                boxs.append([x, []])
            conf['mailbox'] = [unicode(incf['name']), boxs]
            
        userpath = os.path.join(self.datadir, name)
        if not os.path.isdir(userpath):
            os.mkdir(userpath)
        infopath = os.path.join(userpath, 'mailinfo.db')
        #conf['mailinfo'] = dbtable.DBTable(infopath, self.mailinfo_fields)
        self.db = dbope.DBOpe(infopath)
        self.db.open()
        self.db.execute(self.mailinfo_sql)
        self.db.close()

        self.dump_conf(conf)
        
        self.users[name] = conf
        self.mailboxs[email] = conf

        return conf
     
    def user_delete(self, name):
        conf = self.users[name]
        email = conf['email']
        self.dump_user(name)
        
        del self.users[name]
        del self.mailboxs[email]
        
        userdir = os.path.join(self.datadir, name)
        del conf
        os.rename(userdir, userdir+'.%d.bak' % (int(time.time())))

    
    def load(self):
        self.linkman = linkman.LinkMan(self.datadir)

        boxes = os.listdir(self.datadir)
        for box in boxes:
            if box.endswith(".bak"): # ignore dir name end with .bak
                continue
            conf_path = os.path.join(self.datadir, box, 'config.db')
            if not os.path.isfile(conf_path):
                continue
            else:
                f = open(conf_path, 'r')
                conf = pickle.load(f)
                f.close()
                
            mailinfo_path   = os.path.join(self.datadir, box, "mailinfo.db")
            #mailinfo   = dbtable.DBTable(mailinfo_path, self.mailinfo_fields, self.mailinfo_index)
            #userconf = {'config': conf, 'mailinfo':mailinfo}
            self.users[conf['name']] = conf
            self.mailboxs[conf['email']] = conf

            loginfo(mypprint.pformat(conf['mailbox']))
    
    def load_conf(self, name):
        conf_path = os.path.join(self.datadir, name, 'config.db')
        f = open(conf_path, 'r')
        conf = pickle.load(f)
        f.close()
        return conf
                
            
    def dump_conf(self, cf):
        if type(cf) == types.StringType or type(cf) == types.UnicodeType:
            cf = self.users[cf]
        confpath = os.path.join(self.datadir, cf['name'], 'config.db')
        f = open(confpath, 'w')
        pickle.dump(cf, f)
        f.close()
    
    def dump_user(self, name):
        conf = self.users[name]
        self.dump_conf(conf)
        
    def dump_all(self):
        for u in self.users:
            self.dump_user(u)
          
def load():
    global cf
    app = AppConfig()
    app.load()
    #print 'load users:', app.users        
    cf = app

def test():
    global cf
    app = AppConfig()
    app.load()
    
    # for test
    u = {}
    u['name'] = 'test1'
    u['email'] = 'python25@163.com'
    u['password'] = sys.argv[1]
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

if __name__ == '__main__':
    test()
else:
    load()

