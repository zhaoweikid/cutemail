# -*- encoding: utf-8 -*-
import string, os, sys
import wx, threading, time, traceback, base64
import config, dbope
import pop3, sendmail

class Schedule(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_running = True
        self.last_uptime = 0
        self.tasks = []
   
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

    def update_config(self):
        '''
        action:  id: xxxxx, alert: alter string
                 desc: string
                 type: [smtp, arg]/[recvmail,arg]/[msgbox,arg]
        '''
        # 每5分钟更新一次配置
        if time.time() - self.last_uptime < 300:
            return
        #res = config.cf.db.select('schedule', ['timer', 'action'])
        #for item in res:
        #   ts = parse_time(res[0])
        #   self.tasks.append([ts, json.read(res[1])])
                
    def check_time(self, taskt):
        t1 = time.localtime()
        t = [t1[4], t1[3], t1[2], t1[1], t1[6]]
        
        for i in range(0, len(t)):
            if not taskt[i]:
                continue
            if t[i] not in taskt:
                return False
        return True
        
    def run(self):
        threadname = threading.currentThread().getName()
        while self.is_running:
            # 读取任务
            self.update_config()
            
            #print threadname, len(self.tasks)
            time.sleep(1)
            t1 = time.localtime()
            t = [t1[4], t1[3], t1[2], t1[1], t1[6]]
            # 循环获取任务列表里的任务
            for x in range(0, len(self.tasks)):
                k = self.tasks[x][0] #任务执行时间
                v = self.tasks[x][1] #任务参数
                
                ispass = self.check_time(k)
                
                if ispass:
                    # run task ...
                    tid = int(time.time())*10 + x
                    v['id'] = tid
                    if v['alert']:
                        req = {'id':tid, type:'alert', text:v['alert']}
                        config.msgin.put(req)
                        rep = config.msgout.get()
                        if not rep['result']:
                            continue 
                    
                    config.taskq.put(v)
                    print 'put task ok!'
                     
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
                print 'task type not found'
            else:
                func(item)
            
    
    def recvmail(self, item):
        name = item['name']
        try:
            ucf = config.cf.users[name]
        except:
            print 'get user config error!'
            return
        print ucf
        mailinfos = []
        try:
            pop = pop3.POP3Client(ucf)
            pop.init()
            pop.login()
            pop.infos()
            mailinfos = pop.mails()
            pop.close()
        except Exception, e:
            error = str(e)
            traceback.print_exc()
    
        dbpath = os.path.join(config.cf.datadir, name, 'mailinfo.db')
        conn = dbope.DBOpe(dbpath)
        for minfo in mailinfos:
            attachs = []
            for x in minfo['attach']:
                attachs.append('::'.join(x))
            attachstr = '||'.join(attachs)
            
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
                traceback.print_exc()
        conn.close()
        print config.cf.users[name]
        # 有可能有冲突
        config.cf.dump_conf(name)
        print 'recvmali complete!'
        x = {'name':name, 'task':'updatebox', 'message':''}
        config.uiq.put(x, timeout=5)
    
    def sendmail(self, item):
        tos = item['to']

        x = sendmail.SendMailMX(item['from'], item['to'])
        f = open(item['path'], 'r')
        s = f.read()
        f.close()
        try:
            x.send(s)
        except Exception, why:
            mesg = str(why)
        else:
            mesg = u'发送成功'
        x = {'name': item['name'], 'task':'alert', 'message':mesg} 
   
        config.uiq.put(x, timeout=5)


