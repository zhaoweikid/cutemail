# coding: utf-8
import os, sys, time
import traceback
import threading

class RWLock:
    def __init__(self):
        self.cond = threading.Condition()
        self.idc = 0
        
        self.rcount = set()
        self.wcount = set()
        self.write_wait = False

    def acquire_read(self):
        self.cond.acquire()
        #print 'read wcount:', self.wcount, 'rcount:', self.rcount
        while len(self.wcount) > 0 or self.write_wait:
            try:
                #print 'read wait ...'
                self.cond.wait()
            except Exception, e:
                traceback.print_exc()
                #print 'wait error:', e
        self.idc += 1
        rid = self.idc
        self.rcount.add(rid)
        self.cond.release()

        return rid
    
    def acquire_write(self):
        self.cond.acquire()
        self.write_wait = True
        #print 'write wcount:', self.wcount, 'rcount:', self.rcount
        while len(self.wcount) + len(self.rcount) > 0:
            try:
                self.cond.notify()
                #print 'write wait ...'
                self.cond.wait()
            except:
                pass
        self.idc += 1
        wid = self.idc
        self.wcount.add(wid)
        self.write_wait = False
        self.cond.release()

        return wid
 
    def release_read(self, rid):
        self.cond.acquire()
        #print 'release read:', rid
        try:
            self.rcount.remove(rid)
        except:
            pass
        self.cond.notifyAll()
        self.cond.release()

    def release_write(self, wid):
        self.cond.acquire()
        #print 'release read:', wid
        try:
            self.wcount.remove(wid)
        except:
            pass
        self.cond.notifyAll()
        self.cond.release()

    def acquire(self, way='r'):
        if way == 'r':
            return self.acquire_read()
        else:
            return self.acquire_write()

    def release(self, rid, way='r'):
        if way == 'r':
            self.release_read(rid)
        else:
            self.release_write(rid)

def test1(lock):
    while True:
        a = lock.acquire_read() 
        print 'acquire read id:', a
        time.sleep(1)
        lock.release_read(a)

def test2(lock):
    while True:
        a = lock.acquire_write() 
        print 'acquire write id:', a 
        time.sleep(1)
        lock.release_write(a)

def test():
    lock = RWLock()
    
    t1 = threading.Thread(target=test1, args=(lock,))
    t2 = threading.Thread(target=test1, args=(lock,))
    t3 = threading.Thread(target=test1, args=(lock,))
    t4 = threading.Thread(target=test2, args=(lock,))

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()




if __name__ == '__main__':
    test()



