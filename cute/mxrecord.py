import os, sys, string
import dns.resolver

class MXRecord:
    def __init__(self, domain):
        self.domain = domain
        self.count = 0
        self.mx = []
        self.a = []       
        self._query()
        self.pos = 0

    def is_ip(self, ip):
        #print 'ip: ||'+ip+"||"        
        ips = string.split(ip, ".")
        if len(ips) != 4:
            return False
        try:
            b1 = int(ips[0])
            b2 = int(ips[1])
            b3 = int(ips[2])
            b4 = int(ips[3])
            if b1 > 255 or b1 < 0:
                return False
            if b2 > 255 or b2 < 0:
                return False
            if b3 > 255 or b3 < 0:
                return False
            if b4 > 255 or b4 < 0:
                return False
        except:
            return False        
        return True
      
      
    def _query_a(self, domain):
        answers = dns.resolver.query(domain, 'A')
        #print 'Host ', answers.rrset[0]
        return  str(answers.rrset[0])

    def _query_mx(self, domain):
        mxr = []
        answers = dns.resolver.query(domain, 'MX')
        for rdata in answers:
            #print 'Host', rdata.exchange, 'has preference', rdata.preference
            mxr.append([str(rdata.exchange), str(rdata.preference)])
        return mxr
            
    def _query(self):
        if not self.domain:
            return -1
        try:
            mxr = self._query_mx(self.domain)
        except:
            self.mx = []
            mxr = None
            
        if mxr:
            for r in mxr:
                if r[0][-1] == '.':
                    dom = r[0][0:-1]
                else:
                    dom = r[0]
                if not self.is_ip(dom):
                    #print 'query: ',dom
                    ip = self._query_a(dom)
                else:
                    ip = dom
            
                self.mx.append([ip, dom, int(r[1])])
        
        try:
            aip = self._query_a(self.domain)
        except:
            self.a = []
        else:
            self.a.append([aip, self.domain])
       
            
        if mxr:
            self.count = len(self.mx)
            self.mx.sort(lambda x, y: x[-1]-y[-1])
        else:
            self.count = 0
            
        
        
    def mx_min(self):
        self.pos = 0
        if not self.mx:
            return None
        #self.pos = self.pos  + 1
        return self.mx[0][0]
    
    def mx_count(self):
    
        return self.count
    
    def mx_list(self):
        lst = []
        if not self.mx:
            return []
        for i in self.mx:
            lst.append(i[0])
        return lst

    def mx_next(self):
        self.pos = self.pos + 1
        if not self.mx:
            return None
        return self.mx[0][self.pos]
    
    def record_a(self):
        if not self.a:
            return None
        return self.a[0][0]

    def record_all(self):
        lst = []
        if not self.mx:
            return None
        for i in self.mx:
            lst.append(i[0])
        lst.append(self.a[0][0])

    def __str__(self):
        msg = ""
        if  self.mx:
            for i in self.mx:    
                msg = msg +  "MX: %s %s %s\n" % (i[0], i[1], i[2])
        if self.a:            
            msg = msg + "A:  %s %s\n" % (self.a[0][0], self.a[0][1])
        return msg

    def echo(self):
        if self.mx:
            for i in self.mx:
                print "MX:", i[0], i[1], i[2]
        if self.a:
            print "A: ", self.a[0][0], self.a[0][1]

if __name__ == '__main__':
    rec = MXRecord(sys.argv[1])
    print 'all mx record count: ', rec.mx_count()
    print str(rec)
    print '-----------------------------'
    rec.echo()
    print '-----------------------------'
    print rec.mx_min()

