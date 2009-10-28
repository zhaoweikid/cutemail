from distutils.core import setup
import py2exe, glob

files = glob.glob('base/*.py') 
modules = [ k[5:-3] for k in files]
print 'modules:', modules

includes = ["encodings", "encodings.*", 'shutil', 'uuid', 'email', 'email', 'email.*',
            'email.mime.*', 'sqlite3', 'poplib', 'smtplib', 'cute']
options = {"py2exe":
            {   "compressed": 0,
                #"optimize": 2,
                "includes": includes,
                "excludes": modules,
            }
          }
setup(  
    version = "0.8.6",
    description = "cutemail",
    name = "CuteMail",   
    data_files = [('bitmaps/16', glob.glob('./bitmaps/16/*.*')), 
                  ('bitmaps/32', glob.glob('./bitmaps/32/*.*')),
                  ('bitmaps/mailbox', glob.glob('./bitmaps/mailbox/*.*')),
                  ('bitmaps', glob.glob('./bitmaps/*.*')), 
                  ('base', glob.glob('./base/*.py')),
                  ('cute', glob.glob('./cute/*.py'))],
    options = options,   
    windows=[{"script": "cutemail.py", "icon_resources": [(1, "bitmaps/cutemail.ico")] }],     
    )
