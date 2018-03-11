#!/usr/bin/python

import json
import sqlite3

DEBUG = True
dbFname = "parkrun.db"

def addRunner(idRec,conn):
    if (DEBUG): print idRec
    nameStr = idRec['name']
    id = int(idRec['id'])
    if(DEBUG): print "addRunner - id=%d, nameStr =%s." % (id,nameStr) 
    sqlStr = "select id,name from runners where id=?"
    if(DEBUG): print "addRunner - sqlStr =%s." % sqlStr 
    cursor = conn.execute(sqlStr,(id,))
    rows = cursor.fetchall()

    if (len(rows)>0):
        print rows[0]
        if (DEBUG): print "Runner %s already exists as ID %d" % (rows[0][1],rows[0][0])
    else:
        if (DEBUG): print "Runner not found - adding to DB"
        sqlStr = "insert into runners (id,name,created,modified) values (?,?,date('now'),date('now'))"
        if(DEBUG): print "addRunner - sqlStr =%s." % sqlStr 
        cursor = conn.execute(sqlStr,(id,nameStr,))
        if (DEBUG): print "Added %s as ID %d" % (nameStr,cursor.lastrowid)
        conn.commit()


conn = sqlite3.connect(dbFname)
f = open('iddb.json','r')
iddb = json.load(f)
f.close()

for idrec in iddb:
    #print part['name']
    addRunner(idrec,conn)


