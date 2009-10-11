# coding: utf-8
import os, string, sys, time
import types, locale, traceback
import threading

logobj  = None

class FileLogger:
    def __init__(self, logfile='',
                logsize=0, logcount=0, end='\n'):
        self.logfile = ''
        if logfile:
            self.logfile = os.path.abspath(logfile)
        self.log = None

        self.logsize  = logsize
        self.logcount = logcount
        self.lasttime = time.time()

        self.end = end
        self.charset = 'gbk' 
        self.lock = threading.Lock()
        self.open()

        x = locale.getdefaultlocale()
        self.info("locale:", x) 
        self.log.flush()

        if x and x[1]:
            if x[1].find('MAC') >= 0:
                self.charset = 'utf-8'
            else:
                self.charset = x[1]


    def open(self):
        self.log = sys.stdout

        if self.logfile:
            self.log = open(self.logfile, 'a+')
            sys.stdout = self.log
            sys.stderr = self.log
        
    def close(self):
        self.log.flush()
        if self.log != sys.stdout:
            self.log.close()
            self.log = None

    def rotate(self):
        def mysort(a, b):
            if a[0] > b[0]:
                return 1
            elif a[0] < b[0]:
                return -1
            return 0
        if self.logsize > 0 and self.logfile and os.path.isfile(self.logfile):
            size = os.path.getsize(self.logfile)
            #print 'size:', size, 'logsize:', self.logsize
            if size < self.logsize:
                return
            newname = self.logfile + '.%04d%02d%02d.%02d%02d%02d' % time.localtime()[:6]
            self.log.close()
            self.log = None
            #print 'rename ', self.logfile, newname
            os.rename(self.logfile, newname)
            #self.lasttime = time.time()
            self.open()
    
    def writex(self, level='inf', *s):
        if level == 'inf':
            color = '\33[37m'
        elif level == 'warn':
            color = '\33[32m'
        elif level == 'err':
            color = '\33[31m'
        else:
            return

        s = list(s)
        for k in xrange(0, len(s)):
            v = s[k]
            if type(v) == types.UnicodeType:
                s[k] =  v.encode(self.charset)
            elif type(v) != types.StringType:
                s[k] = str(v)
            else:
                s[k] = str(v)

        infos = traceback.extract_stack()[-4]
        ifs = string.split(infos[0], os.sep)
        filename = ifs[-1]
        line = infos[1]

        if not self.logfile:
            ss = '%d%02d%02d %02d:%02d:%02d '  % time.localtime()[:6]
            ss = '%s%s%s %s:%d [%s] %s\33[0m%s' % (color, ss, threading.currentThread().getName(), filename, line, level, ' '.join(s), self.end)
        else:
            ss = '%d%02d%02d %02d:%02d:%02d ' % time.localtime()[:6]
            ss += '%s %s:%d [%s] %s%s' % (threading.currentThread().getName(), filename, line, level, ' '.join(s), self.end)
        
        timenow = time.time()
        if self.logfile and timenow - self.lasttime > 10:
            size = os.path.getsize(self.logfile)
            
            if self.logsize > 0 and size > self.logsize:
                self.lock.acquire()
                try:
                    self.rotate()
                except Exception, e:
                    traceback.print_exc()
                self.lock.release()
            self.lasttime = timenow

        self.log.write(ss)
        
        self.log.flush()

    def info(self, *s):
        self.writex('inf', *s)

    def warn(self, *s):
        self.writex('warn', *s)

    def err(self, *s):
        self.writex('err', *s)

    def write(self, s):
        self.writex('info', s)

def loginit(logfile='', logsize=10240000, count=10):
    global logobj
    if logobj:
        logobj.close()
    logobj = FileLogger(logfile, logsize=logsize, logcount=count)

def loginfo(*s):
    global logobj
    logobj.info(*s)

def logwarn(*s):
    global logobj
    logobj.warn(*s)

def logerr(*s):
    global logobj
    logobj.err(*s)

#loginit('cutemail.log')
loginit()

def test():
    for x in xrange(0, 10):
        for i in xrange(0, 100):
            loginfo('hehe, loginfo...')
            logwarn('hehe, logwarn...')
            logerr('hehe, logerr...')

if __name__ == '__main__':
    test()



