# coding: utf-8
import string, os, sys, time, types
from bsddb import db
import cPickle as pickle


class DBTable:
    def __init__(self, tblname, fields=[], index=[]):
        self._fields = fields
        self._name = tblname
        self._index = index
        self._fields_hash = {}
        
        for i in xrange(0, len(fields)):
            self._fields_hash[fields[i]] = i
        
        self._primary_name = tblname + '.db'
        self._primary = db.DB() 
        self._primary.open(self._primary_name, tblname, db.DB_BTREE, db.DB_CREATE|db.DB_THREAD)
        # secondary = {'index key' : [filename, db]}
        self._secondary = {}
        for x in index:
            filename = tblname + '.' + x + '.idx'
            sec = db.DB()
            sec.set_flags(db.DB_DUPSORT)
            sec.open(filename, x, db.DB_BTREE, db.DB_CREATE|db.DB_THREAD)
            self._secondary[x] = [filename, sec]
            idx = self._fields_hash[x]
            self._primary.associate(sec, lambda a,b: pickle.loads(b)[idx])
        
        self._cursor = None

    def close(self):
        self._primary.sync()
        self._primary.close()
        
        for k in self._secondary:
            x = self._secondary[k]
            sec = x[1]
            sec.close()
    
    def sync(self):
        self._primary.sync()

    def insert(self, values):
        if type(values) == types.ListType:
            self._primary[values[0]] = pickle.dumps(values)
        elif type(values) == types.DictType:
            v = []
            for k in self._fields:
                v.append(values[k])
            self._primary[v[0]] = pickle.dumps(v)

    def insert_many(self, values):
        for row in values:
            self.insert(row)

        self._primary.sync()

    def operation(self, row, cond):
        v  = row[cond[0]]
        op = cond[1]
        value = cond[2]

        if op == '=':
            return v == value
        elif op == '!=':
            return v != value
        elif op == 'prefix':
            return v.startswith(value)
        elif op == 'postfix':
            return v.endswith(value)
        elif op == 'like':
            return v.find(value) >= 0
        elif op == '>':
            return int(v) > int(value)
        elif op == '>=':
            return int(v) >= int(value)
        elif op == '<':
            return int(v) < int(value)
        elif op == '<=':
            return int(v) <= int(value)
        else:
            return False
        

    def select(self, conditions=[]):
        '''conditions = [[index1, op, value1], [index2, op, value2]]
           fields: [k1, k2, k3] / [0, 3, 4]
           op: = > >= < <= != prefix postfix like
        '''
        rows = []
        innercond = []
        for i in xrange(0, len(conditions)):
            item = conditions[i]
            innercond.append([self._fields_hash[item[0]], item[1], item[2]])

        cur = self._primary.cursor()
        rec = cur.first()
        while rec:
            x = pickle.loads(rec[1])
            for cond in innercond:
                if self.operation(x, cond):
                    rows.append(x)
            if not innercond:
                rows.append(x)
            rec = cur.next()
        cur.close()

        return rows


    def update(self, values, conditions={}):
        '''values = [[key, val], ...]'''
        innercond = []
        for item in conditions:
            innercond.append([self._fields_hash[item[0]], item[1], item[2]])

        innerkey = []
        for item in values:
            innerkey.append([self._fields_hash[item[0]], item[1]])
        
        cur = self._primary.cursor()
        rec = cur.first()
        while rec:
            x = pickle.loads(rec[1])
            for cond in innercond:
               if self.operation(x, cond):
                    for item in innerkey:
                        x[item[0]] = item[1]
                    cur.put(rec[0], pickle.dumps(x), db.DB_CURRENT)
            rec = cur.next()
        cur.close()


    def delete(self, conditions={}):
        innercond = []
        for i in xrange(0, len(conditions)):
            item = conditions[i]
            innercond.append([self._fields_hash[item[0]], item[1], item[2]])

        cur = self._primary.cursor()
        rec = cur.first()
        while rec:
            x = pickle.loads(rec[1])
            for cond in innercond:
                if self.operation(x, cond):
                    cur.delete()
            rec = cur.next()
        cur.close()

 
   
    def get(self, pair):
        '''pair = [k, v]'''
        if type(pair) == types.ListType:
            k = pair[0]
            v = pair[1]
        
            pos = self._fields_hash[k]
            if pos == 0:
                return pickle.loads(self._primary[v])
            indexdb = self._secondary[k][1]
            return pickle.loads(indexdb[v])
        elif type(pair) == types.StringType:
            return pickle.loads(self._primary[pair])
        
    def get_primary_db(self):
        return self._primary

    def get_secondary_db(self, index):
        return self._secondary[index][1]

    def delete_key(self, pair):
        if type(pair) == types.ListType:
            k = pair[0]
            v = pair[1]
            
            pos = self._fields_hash[k]
            if pos == 0:
                self._primary.delete(v)
                return
            indexdb = self._secondary[k][1]
            indexdb.delete(v)
            return
        elif type(pair) == types.StringType:
            self._primary.delete(pair)
            return
             
    '''note: methods below not thread safe'''
    def reset(self):
        if self._cursor:
            self._cursor.close()
        self._cursor = self._primary.cursor()
    
    def first(self):
        return self._cursor.first()

    def last(self):
        return self._cursor.last()

    def next(self):
        return self._cursor.next()

    
def test():
    tbl = DBTable("testdb", ['id', 'name', 'age', 'sex'], ['name'])
    tbl.insert(['1', 'zhaowie', '12', 'fa'])
    tbl.insert(['2', 'zhaowei', '18', 'm'])
    print 'get 1:', tbl.get('1')
    print 'select all:', tbl.select()
    print 'select 1:', tbl.select([['id', '=', '1']])
    tbl.update([['name','bobo']], [['id', '=', '2']])
    print 'after update select all:', tbl.select()
    tbl.delete([['id', '=', '1']])
    print 'after delete select all:', tbl.select()
    tbl.delete_key(['name','bobo'])
    print 'after delete_key select all:', tbl.select()
    tbl.close()

def test2():
    tbl = DBTable("testdb", ['id', 'name', 'age', 'sex'], ['name'])
    start = time.time()
    for i in xrange(0, 10000):
        tbl.insert([str(i), 'zhaowei'+str(i), str(i+10), 'm'])
    end = time.time()
    print 'insert 10000 time:', end-start
    
    start = time.time()
    for i in xrange(0, 10000):
        tbl.get(str(i))
    end = time.time()
    print 'get 10000 time:', end-start

    start = time.time()
    for i in xrange(0, 100):
        tbl.select([['id', '=', str(i)]])
    end = time.time()
    print 'select 100 time:', end-start


    tbl.close()

if __name__ == '__main__':
    test()

