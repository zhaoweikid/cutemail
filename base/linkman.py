# coding: utf-8
import os, sys
import cPickle as pickle
import config
import logfile
from logfile import loginfo, logwarn, logerr

class LinkManSync:
    def __init__(self):
        pass

    def get(self, mailaddr):
        pass



class LinkMan:
    def __init__(self, user):
        self.user = user
        self.defgroups = [u'最近联系人', u'我的好友', u'我的同事', u'其他联系人']
        self.defuserinfo = [u'head', u'手机', u'qq', u'msn', u'家庭电话', u'单位电话', u'生日']
        # {'groupname':[], u'最近联系人':[[u'赵威', 'zhaoewikid@163.com', {'head':'',u'手机':'',u'qq':'','msn':'','家庭电话':'','单位电话':''}], ], }
        self.groups = {}
        self.index_email = {}
    
    def load(self):
        fpath = os.path.join(config.cf.datadir, self.user, 'linkman.cf')
        if not os.path.isfile(fpath) or os.path.getsize(fpath) == 0:
            self.groups['groupname'] = self.defgroups
            for k in self.defgroups:
                self.groups[k] = []
            return
        f = open(fpath ,'r')
        x = pickle.load(f)
        f.close()

        self.groups = x
        for k in x:
            if k == 'groupname':
                continue
            v = x[k]
            for item in v:
                self.index_email[item[1]] = item

    def dump(self):
        fpath = os.path.join(config.cf.datadir, self.user, 'linkman.cf')
        f = open(fpath, 'w')
        pickle.dump(self.groups, f)
        f.close()
   
    def add(self, name, email, group=None, other=None):
        if self.index_email.has_key(email):
            raise ValueError, 'email is exists'
        info = dict(zip(self.defuserinfo, ['']*len(self.defuserinfo)))
        if other:
            info.update(other)
        if group:
            gpname = group
        else:
            gpname = u'其他联系人'
        x = [name, email, gpname, info] 

        loginfo('groups:', self.groups)
        loginfo('gpname:', gpname)
        self.groups[gpname].append(x)
        self.index_email[email] = x

        self.dump()

        return x

    def delete(self, email):
        if not self.index_email.has_key(email):
            return
        x = self.index_email[email]
        del self.index_email[email]
        
        for k in self.groups:
            if k == 'groupname':
                continue
            v = self.groups[k]
            found = -1
            for i in xrange(0, len(v)):
                item = v[i]
                if item[1] == email:
                    found = i
                    break
            if found >= 0:
                del v[i]
                break
        x = None 

    def find_by_email(self, email):
        return self.index_email[email]


    def find_by_name(self, name):
        for k in self.groups:
            if k == 'groupname':
                continue
            v = self.groups[k]
            for item in v:
                if item[0] == name: 
                    return item
        return None

    def find_email_part(self, email):
        ret = []

        for k in self.groups:
            if k == 'groupname':
                continue
            v = self.groups[k]
            for item in v:
                if item[1].startswith(email): 
                    ret.append(item[1]) 
        return ret

def test():
    import pprint
    print 'test linkman'
    m = LinkMan('zhaowei')
    m.load()
    pprint.pprint(m.groups)
    m.add('bobo', 'rabbit_haobobo@163.com', u'我的好友')
    pprint.pprint(m.groups)
    m.dump()

if __name__ == '__main__':
    print '-'*60
    test()



