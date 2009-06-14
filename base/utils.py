import string, sys, os

def maildir_init(dpath, hash_count=10):
    if not os.path.isdir(dpath):
        os.mkdir(dpath)
    for i in xrange(0, hash_count):
        xpath = dpath + os.sep + '%02d' % (i)
        if not os.path.isdir(xpath):
            os.mkdir(xpath)
            
            