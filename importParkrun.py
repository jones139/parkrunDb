#!/usr/bin/python

import json

def findId(nameStr,iddb):
    id='unknown'
    #print "findId - nameStr =%s." % nameStr 
    for idrec in iddb:
        #print part['name']
        if idrec['name'] == nameStr and idrec['id']!= 'unknown':
            id = idrec['id']
    return id

f = open('partlist.json','r')
partList = json.load(f)
f.close()
f = open('iddb.json','r')
iddb = json.load(f)
f.close()

for part in partList:
    if part['id'] == 'unknown':
        #print 'searching for %s' % part['name']
        id = findId(part['name'],iddb)
        #print '   found id=%s' % id
        part['id'] = id

print "search finished...."
for part in partList:
    if part['id'] == 'unknown':
        print 'name %s not found' % part['name']

print "writing partitipants list..."        
f = open('partlist.json','w')
json.dump(partList,f,indent=2, separators=(',', ': '))
f.close()
