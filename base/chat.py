# coding: utf-8
import os, sys, time
import socket, threading
import Queue
import simplejson
import logfile
from logfile import loginfo, logwarn, logerr

receq = {}
sendq = Queue.Queue()

class Chat:
    def __init__(self):
        self.addr = ('0.0.0.0', 10010) 
        self.email = ''
        self.clients = {}
        self.isrunning = True

        self.init()

    def init(self):
        self.broadcast()
        self.listentcp()

        th1 = threading.Thread(target=self.recevier) 
        th2 = threading.Thread(target=self.sender) 
        th1.start()
        th2.start()

    def broadcast(self):
        self.localudp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.localudp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.localudp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.localudp.bind(self.addr)
    
    def listentcp(self):
        self.localtcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.localtcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.localtcp.bind(self.addr)
        self.localtcp.listen(32)

    def recevier(self):
        '''
        cmd: me  发现服务
        cmd: msg message
        message: {'cmd':'','msg':'','from':'','to':'','time':''}
        '''
        x = {'cmd':'new', 'msg':self.email, 'from':self.email, 'to':'', 'time':int(time.time())}
        self.localudp.sendto(simplejson.dumps(x), ('<broadcast>', 10010)) 

        while self.isrunning:
            #loginfo('recevied get.')
            data, addr = self.localudp.recvfrom(4096)
            loginfo('recv:', data, 'addr:', addr)
            x = simplejson.loads(data)
            cmd = x['cmd']
            if cmd == 'me':
                loginfo('add to clients:', x['from'], addr)
                self.clients[x['from']] = addr
            elif cmd == 'msg':
                receq[x['from']].put(x)
            elif cmd == 'new':
                loginfo('add to clients:', x['from'], addr)
                self.clients[x['from']] = addr

    def sender(self):
        while self.isrunning:
            #loginfo('sender  get.')
            try:
                x = sendq.get(timeout=5)
            except:
                continue
            loginfo('send:', x)

            if x['cmd'] == 'onlinestatus':
                #x['cmd'] = 'onlinestatus'
                loginfo('check clients:', self.clients)
                if self.clients.has_key(x['to']):
                    x['msg'] = 'online' 
                else:
                    x['msg'] = 'offline' 

                receq[x['to']].put(x)
            elif x['cmd'] == 'msg':
                if not self.clients.has_key(x['to']):
                    x['error'] = 'not found user'
                    receq[x['to']].put(x)
                    continue
                addr = self.clients[x['to']]
                msg = simplejson.dumps(x)
                self.localudp.sendto(msg, addr)

def test():
    email = 'zhaoweikid@163.com'
    c = Chat(email)
    loginfo('me:', email)

    while True:
        time.sleep(10)

if __name__ == '__main__':
    test()



