# coding: utf-8
import os, sys
import subprocess

VERSION = "0.8"

def check_version():
    cmd = "hg tip"
    f = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    line = f.stdout.readline()
    num = line.strip().split()[1].split(':')[0]
    version = VERSION + "." + num
    print 'version:', version

    f = open("cutemail.nsi", "r")
    lines = f.readlines()
    f.close()
    
    name = ''
    fullname = ''
    for line in lines:
        if line.startswith('Name'):
            name = line.strip().split()[1][1:-1]
            fullname = '%s_%s.exe' % (name, version)
            break 
    if not fullname:
        return

    f = open('cutemail.nsi', 'w')
    for line in lines:
        if line.startswith('OutFile'):
            f.write('OutFile "%s"\n' % (fullname))
        else:
            f.write(line)


check_version()


