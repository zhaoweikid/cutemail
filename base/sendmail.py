#coding: UTF-8
import smtplib, base64, string
import DNS, socket, sys, traceback

class MySMTP(smtplib.SMTP):
    def connect(self, host='localhost', port = 0):
        if not port and (host.find(':') == host.rfind(':')):
            i = host.rfind(':')
            if i >= 0:
                host, port = host[:i], host[i+1:]
                try: port = int(port)
                except ValueError:
                    raise socket.error, "nonnumeric port"
        if not port: port = SMTP_PORT
        if self.debuglevel > 0: print>>stderr, 'connect:', (host, port)
        msg = "getaddrinfo returns an empty list"
        self.sock = None
        for res in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.sock = socket.socket(af, socktype, proto)
                if self.debuglevel > 0: print>>stderr, 'connect:', sa
                self.sock.settimeout(3)
                self.sock.connect(sa)
            except socket.error, msg:
                if self.debuglevel > 0: print>>stderr, 'connect fail:', msg
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue
            break
        if not self.sock:
            raise socket.error, msg
        (code, msg) = self.getreply()
        if self.debuglevel > 0: print>>stderr, "connect:", msg
        return (code, msg)

class SessionError(Exception):
    def __repr__(self):
        return self.message

class SendMail:
    def __init__(self, smtp_server, from_addr, to_addr):
        self.fromaddr = from_addr
        self.toaddr = to_addr
        self.svr = None
        self.mailserver_port = 25

        if smtp_server:
            ipport = string.split(smtp_server, ":")
            if len(ipport) == 2:
                self.mailserver = ipport[0]
                self.mailserver_port = ipport[1]
            else:
                self.mailserver = smtp_server

    def helo(self):
        self.svr = MySMTP(self.mailserver, self.mailserver_port)
        self.svr.set_debuglevel(1)
        code, msg = self.svr.docmd("HELO server")
        if code >= 400 or code >= 500:
            raise SessionError, str(code) + msg

    def ehlo(self, passwd):
        self.svr = MySMTP(self.mailserver, self.mailserver_port)
        self.svr.set_debuglevel(1)
        password = string.strip(base64.encodestring(passwd))
        username = string.strip(base64.encodestring(self.fromaddr))
        self.svr.docmd("EHLO x")
        self.svr.docmd("AUTH LOGIN")
        self.svr.docmd(username)
        code, msg = self.svr.docmd(password)
        if code >= 400 or code >= 500:
            raise SessionError, str(code) + msg

    def mail_from(self):
        code, msg = self.svr.docmd("MAIL FROM: <%s>" % self.fromaddr)
        if code >= 400 or code >= 500:
            raise SessionError, str(code) + msg

    def rcpt_to(self):
        error = 0
        for to in self.toaddr:
            code, msg = self.svr.docmd("rcpt to: <%s>" % to)
            if code >= 400 or code >= 500:
                error = 1
                continue
        if error == 1:
            err = "rctp_to errors"
            raise SessionError, err 

    def data(self, message):
        code, msg = self.svr.docmd("DATA")
        self.svr.set_debuglevel(0)
        self.svr.send(message)
        self.svr.send("\r\n.\r\n")
        self.svr.set_debuglevel(1)
        self.svr.getreply()

    def authsend(self, message, passwd):
        self.ehlo(passwd)
        self.mail_from()
        self.rcpt_to()
        self.data(message)

    def send(self, message):
        self.helo() 
        self.mail_from()
        self.rcpt_to()
        self.data(message)

class SendMailServer(SendMail):
    def __init__(self, smtp_server, fromaddr, toaddr):
        SendMail.__init__(smpt_server, fromaddr, toaddr)

    def srv_authsend(self, message, passwd):
        try:
            self.authsend(message, passwd)

        except socket.error,e:
            traceback.print_exc()
        except SessionError, e:
            traceback.print_exc()

    def srv_send(self, message):
        try:
            self.send(message)
        except socket.error,e:
            traceback.print_exc()
        except SessionError, e:
            traceback.print_exc()
        
class SendMailMX(SendMail):
    def __init__(self, fromaddr, toaddr):
        self.from_addr = fromaddr
        self.to_addr = toaddr

    def dns_analysis(self, domain):
        DNS.ParseResolvConf()

        r = DNS.Request(qtype = 'mx')
        res = r.req(domain)

        return res.answers

    #解析域名，并且对mx记录进行优先级排序，得到排序后mx记录列表
    def get_mx(self, domain):
        mx_list = self.dns_analysis(domain)
        print "debug mx_list"
        print mx_list

        #mx_dic结构：{域名：优先级}
        mx_dic = {}
        mx = []
        if mx_list:
            for item in mx_list:
                print 'debug item'
                print item 
                mx_dic[item['data'][1]] = item['data'][0]

            m = mx_dic.items()
            m.sort(key = lambda x: x[1])
            for item in m:
                mx.append(item[0])
            return mx

        else:
            return None

    def send(self, message):
        #to_addr是要发送的列表
        for to in self.to_addr:
            #得到排序后的mx记录列表
            mx = self.get_mx((string.split(to, '@')[1].strip()))

            succ_flag = 0 
            for item in mx:
                to_list = []
                to_list.append(to)
                sendmail = SendMail(item, self.from_addr, to_list)
                try:
                    sendmail.send(message) 
                    break
                except socket.error, e:
                    traceback.print_exc()
                    continue



if __name__ == '__main__':
    #print "----------------- authsend test ------------------------"
    #auth_test = ServerSend ("mail.eyou.net", "lanwenhong@eyou.net", ["rubbish_lan@sohu.com","lanwenhong12@163.com","yangyang@eyou.net"])
    #auth_test.svr_authsend("subject: test \r\nfrom: lanwenhong@eyou.net\r\nto: rubbish_lan@sohu.com\r\n\r\nthis is test\n", "baozou123")

    #print "----------------- send     test ------------------------"
    #test = ServerSend("mail.eyou.net", "lanwenhong@eyou.net", ["rubbish_lan@sohu.com","lanwenhong12@163.com","yangyang@eyou.net"])
    #test.svr_send("subject: test \r\nfrom: lanwenhong@eyou.net\r\nto: rubbish_lan@sohu.com\r\n\r\nthis is test\n")

    print "----------------- noserversend  ------------------------"
    noserver = NoserverSend("lanwenhong@eyou.net", ["yangyang@eyou.net", "zhaowei@eyou.net", "lanwenhong12@163.com", "bijisheng@eyou.net"])
    noserver.send("subject: test \r\nfrom: lanwenhong@eyou.net\r\nto: rubbish_lan@sohu.com\r\n\r\nthis is test\n")


