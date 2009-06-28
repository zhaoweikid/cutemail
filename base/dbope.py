# coding: utf-8
import os, sys, sqlite3

class DBOpe:
    def __init__(self, dbpath):
        self.conn = None
        self.path = dbpath

    def open(self):
        self.conn = sqlite3.connect(self.path)

    def close(self):
        self.conn.close()
        self.conn = None

    def execute(self, sql):
        self.conn.execute(sql)
        self.conn.commit()

    def query(self, sql):
        cur = sef.conn.cursor()
        cur.execute(sql)
        ret = cur.fetchall()
        cur.close()
        return ret


