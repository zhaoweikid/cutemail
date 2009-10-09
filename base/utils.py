import string, sys, os, shutil
import uuid, time
import logfile, config, mailparse, utils, dbope
from logfile import loginfo, logwarn, logerr
import wx

def maildir_init(dpath, hash_count=10):
    if not os.path.isdir(dpath):
        os.mkdir(dpath)
    for i in xrange(0, hash_count):
        xpath = dpath + os.sep + '%02d' % (i)
        if not os.path.isdir(xpath):
            os.mkdir(xpath)
            
def mailbox_find(mailbox, names):
    cur = mailbox[1]
    lastitem = None
    paths = names[1:]
    for n in paths:
        found = False
        for item in cur:
            if item[0] == n:
                found = True
                cur = item[1]
                lastitem = item
                break
        if not found:
            return None
    return lastitem

def mailbox_find_parent(mailbox, names):
    return mailbox_find(mailbox, names[:-1])

def mailbox_remove(mailbox, names):
    parent = mailbox_find_parent(mailbox, names)
    loginfo('parent:', parent)
    box = names[-1]
    found = False
    childs = parent[1]
    for i in range(0, len(childs)):
        x = childs[i]
        if x[0] == box:
            found = True
            break
    if not found:
        raise ValueError, 'not found mailbox'
    del childs[i]
    
def mailbox_rename(mailbox, names, newname):
    item = mailbox_find(mailbox, names)
    if not item:
        return
    item[0] = newname

def mailbox_add(mailbox, names, addname):
    item = mailbox_find(mailbox, names)
    item[1].append([addname, []])
    
def mailbox_path_to_list(path):
    parts = path.split('/')
    del parts[0]
    return parts
    
    
def mail_import(user, boxnode, filename):
    hashdir_count = 10
    info = mailparse.decode_mail(filename)
    
    attachs = []
    for x in info['attach']:
        attachs.append('::'.join(x))
    attachstr = '||'.join(attachs)
        
    att = 0
    if len(info['attach']) > 0:
        att = 1
    if boxnode['boxname'].find('/') == -1:
        mailbox = config.cf.mailbox_map_cn2en[boxnode['boxname']]
    else:
        return
    info['mailbox'] = mailbox
    info['ctime'] = 'datetime()'
    info['user'] = user

    fname = uuid.uuid1().urn[9:]
    hashdir = '%02d' % (hash(fname) % hashdir_count)
    timepath = '%d%02d' % time.localtime()[:2]
    newdir = os.path.join(config.cf.datadir, user, mailbox, timepath, hashdir)
    if not os.path.isdir(newdir):
        os.makedirs(newdir)
    newfilename = os.sep + os.path.join(timepath, hashdir, '%d.' % (int(time.time())) + fname + '.eml')
    dstfile = os.path.join(newdir, '%d.' % (int(time.time())) + fname + '.eml')
    
    info['filename'] = newfilename
    subject = info['subject'].replace("'", "''")
    attach = attachstr.replace("'", "''")
    
    sql = "insert into mailinfo(filename,subject,mailfrom,mailto,size,ctime,date,attach,mailbox,status) values " \
          "('%s','%s','%s','%s',%d,%s,'%s','%s','%s','noread')" % \
          (newfilename, subject, info['from'], ','.join(info['to']), info['size'],
           info['ctime'], info['date'], attach, info['mailbox'])
    conn = dbope.openuser(config.cf, user)
    conn.execute(sql)
    conn.close()
    shutil.copyfile(filename, dstfile)
    info['box'] = '/%s/%s' % (user, info['mailbox'])
    info['status'] = 'noread'
    info['filepath'] = os.path.join(config.cf.datadir, user, info['mailbox'], info['filename'].lstrip(os.sep))
    item = [info['from'], att, info['subject'], 1, info['date'], str(info['size']/1024 + 1)+' K',wx.TreeItemData(info)]
    panel = boxnode['panel']
    panel.add_mail(item)
   



if __name__ == '__main__':
    import pprint
    a = ['root', [['test1', [['111', ['1111111']],
                             ['a1', ['a1111111']],
                            ]
                  ],
                  ['test2', ['test22']],
                  ['test3', ['test33']]
                 ]
        ]
    pprint.pprint(a)
    
    print 'find:', mailbox_find(a, ['root', 'test1', '111'])
    
    
