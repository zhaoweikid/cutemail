#  -*- encoding: utf-8 -*-
import string, os, sys, simplejson
import wx, threading, time, traceback, base64
import cPickle as pickle
import config, dbope
import pop3, sendmail, logfile
from logfile import loginfo, logwarn, logerr

class Schedule(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_running = True
        self.last_uptime = 0
        self.file_mtime = {}
        # user: [{time:tasktime, param:task param, lasttime:lasttime}]
        self.tasks = {}

        self.load_config()
   
    def parse_time(self, timestr):
        ret = []
        maxv = [59, 23, 31, 12, 6]
        # 分 小时 天 月 周
        s = timestr.split()
        for i in range(0, len(s)):
            x = s[i] 
            # check - / ,
            v = []
            if string.find(x, ',') != -1:
                a = string.split(x, ',')
                v = [ int(b) for b in a]
            elif string.find(x, '-') != -1:
                a = string.split(x, '-')
                for b in range(int(a[0]), int(a[1])+1):
                    v.append(b)
            elif string.find(x, '/') != -1:
                a = string.split(x, '/')
                v = [ int(b) for b in range(int(a[0]), maxv[i]+1, int(a[1]))] 
            else:
                try:
                    a = int(x)
                except: 
                    pass
                else:
                    v.append(a)
            ret.append(v) 
        return ret

    def load_config(self):
        userpath = os.path.join(config.cf.home, 'data')
        users = os.listdir(userpath)
        for u in users:
            if u.endswith('.bak'):
                continue
            ufile = os.path.join(userpath, u, 'config.db')
            mtime = int(os.path.getmtime(ufile))
            if self.file_mtime.has_key(ufile) and self.file_mtime[ufile] == mtime:
                continue
            self.file_mtime[ufile] = mtime

            loginfo('load user config:', u)
            f = open(ufile, 'r')
            s = f.read()
            f.close()

            x = pickle.loads(s)
            
            ts = []
            self.tasks[ufile] = ts
            if x['recv_interval']:
                ri = int(x['recv_interval'])
                trm = range(1, 60, ri)
            else:
                trm = None
            item = {'time':[trm,None,None,None,None], 'param':{'name':u, 'task':'recvmail'}, 'lastrun':int(time.time())}
            loginfo('add task:', item)
            ts.append(item)
        
                
    def check_time(self, taskt):
        t1 = time.localtime()
        t = [t1[4], t1[3], t1[2], t1[1], t1[6]]
        
        ret = False
        for x in taskt:
            ret = ret or x
        if not ret:
            return False

        for i in range(0, len(t)):
            if not taskt[i]:
                continue
            if t[i] not in taskt[i]:
                return False
        return True
        
    def run(self):
        threadname = threading.currentThread().getName()
        while self.is_running:
            # 读取任务
            self.load_config()
            
            #print threadname, len(self.tasks)
            time.sleep(10)
            t1 = time.localtime()
            # 分，小时，日，月，周
            t = [t1[4], t1[3], t1[2], t1[1], t1[6]]
            # 循环获取任务列表里的任务
            for x in self.tasks:
                vals = self.tasks[x]
                #loginfo('values:', vals)
                for item in vals:
                    k = item['time'] #任务执行时间
                    v = item['param'] #任务参数
                
                    ispass = self.check_time(k)
                    
                    tnow = int(time.time())
                    if ispass and tnow - item['lastrun'] >= 60:
                        loginfo('scheduler run task')
                        config.taskq.put(v)
                        item['lastrun'] = tnow 
                        loginfo('put task ok!')
                     
class Task(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_running = True
    
    def run(self):
        threadname = threading.currentThread().getName()
        while self.is_running:
            try:
                item = config.taskq.get(timeout=5)
            except:
                #print threadname, 'not found task'
                continue
            func = getattr(self, item['task'])
            if not func:
                loginfo('task type not found')
            else:
                func(item)
            

    def recvmail(self, item):
        name = item['name']
        try:
            ucf = config.cf.users[name]
        except:
            traceback.print_exc(file=logfile.logobj.log)
            loginfo('get user config error!')
            return
        loginfo('recv mail:', ucf)
        mailinfos = []
        try:
            pop = pop3.POP3Client(ucf)
            pop.init()
            pop.login()
            pop.infos()
            allcount = len(pop.uidls)
            rcount = 0
            while True:
                rcount += 1
                try:
                    minfo = pop.mail()
                    if minfo is None:
                        break
                except:
                    traceback.print_exc(file=logfile.logobj.log)
                    continue
                self.recvmail_one_result(name, minfo, rcount, allcount)

            pop.close()
        except Exception, e:
            error = str(e)
            traceback.print_exc(file=logfile.logobj.log)
    
        # 有可能有冲突
        #config.cf.dump_conf(name)
        loginfo('recvmali complete!')
        #x = {'name':name, 'task':'updatebox', 'message':''}
        #config.uiq.put(x, timeout=5)
   

    def recvmail_one_result(self, name, minfo, rcount, allcount):
        dbpath = os.path.join(config.cf.datadir, name, 'mailinfo.db')
        conn = dbope.DBOpe(dbpath)
 
        attachstr = simplejson.dumps(minfo['attach'])
            
        filename = minfo['filename'].replace("'", "''")
        subject = minfo['subject'].replace("'", "''")
        #plain = minfo['plain'].replace("'", "''")
        #html  = minfo['html'].replace("'", "''")
        attach = attachstr.replace("'", "''")
            
        sql = "insert into mailinfo(filename,subject,mailfrom,mailto,size,ctime,date,attach,mailbox) values " \
              "('%s','%s','%s','%s',%d,%s,'%s','%s','%s')" % \
              (filename, subject, minfo['from'], ','.join(minfo['to']), minfo['size'],
               minfo['ctime'], minfo['date'], attach, minfo['mailbox'])
            
        try:
            conn.execute(sql)
        except:
            traceback.print_exc(file=logfile.logobj.log)
     
        conn.close()
        x = {'name':name, 'task':'newmail', 'message':'', 'filename':filename, 'allcount':allcount, 'count':rcount}
        config.uiq.put(x, timeout=5)
        config.cf.dump_conf(name)

    def sendmail(self, item):
        tos = item['to']
        usercf = config.cf.users[item['name']]
        loginfo('smtp server:', usercf['smtp_server'])
        x = sendmail.SendMail(usercf['smtp_server'], item['from'], item['to'])
        f = open(item['path'], 'r')
        s = f.read()
        f.close()
        try:
            x.authsend(s, usercf['smtp_pass'])
        except Exception, why:
            traceback.print_exc(file=logfile.logobj.log)
            mesg = u'信件发送失败! ' + str(why)
            retval = False
        else:
            mesg = u'信件发送成功!'
            retval = True
 
        x = {'name': item['name'], 'task':'alert', 'message':mesg, 
            'runtask':item['task'], 'return':retval, 'filename':os.path.basename(item['path']),
            'item': item['item']}
   
        config.uiq.put(x, timeout=5)


if __name__ == '__main__':
    s = Schedule()
    s.start() 
    s.join()

