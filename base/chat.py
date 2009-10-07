# coding: utf-8
import os, sys, time
import socket, threading
import Queue
import simplejson
import logfile
from logfile import loginfo, logwarn, logerr

# [fromemail, toemail, cmd, message]
receq = Queue.Queue()
# [fromemail, toemail, cmd, message]
sendq = Queue.Queue()

class Chat:
    def __init__(self, email):
        self.addr = ('0.0.0.0', 10009) 
        self.email = email
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
        self.localtcp.bind(('0.0.0.0', 10010))
        self.localtcp.listen(32)


    
    def recevier(self):
        '''
        cmd: me  发现服务
        cmd: msg message
        message: {'cmd':'','msg':'','from':'','to':'','time':''}
        '''
        self.localudp.sendto('new ' + self.email, ('<broadcast>', 10010)) 

        while self.isrunning:
            data, addr = self.localudp.recvfrom(4096)
            loginfo('recv:', data, 'addr:', addr)
            x = simplejson.loads(data)
            cmd = x['cmd']
            if cmd == 'me':
                self.clients[parts[1]] = addr
            elif cmd == 'msg':
                receq.put(x)
            elif cmd == 'new':
                self.clients[parts[1]] = addr

    def sender(self):
        while self.isrunning:
            try:
                x = sendq.get(5)
            except:
                continue
            loginfo('send:', x)
            if not self.clients.has_key(x['to']):
                x['error'] = 'not found user'
                receq.put(x)
                continue
            addr = self.clients[x['to']]
            msg = simplejson.dumps(x)
            self.localudp.sendto(msg, addr)

def test():
    c = Chat('zhaoweikid@163.com')
    while True:
        try:
            s = receq.get(5)
        except:
            continue
        loginfo('receq:', s)
        
        sendq.put([s[0], 'msg', 'xxxxxxxxx'])

if __name__ == '__main__':
    test()



