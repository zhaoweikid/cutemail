# coding: utf-8
import os, sys

class FoxmailImport:
    def __init__(self, formaildir, username):
        self.foxmaildir = formaildir
        self.user = username
        self.mail_sep = '\x10'*7 + '\x11' * 6 + '\x53' + '\r\n'

    def import_user(self):
        pass


    def import_mail(self):
        pass


    def import_contact(self):
        pass


