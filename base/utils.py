import string, sys, os

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
    print 'parent:', parent
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
    
    