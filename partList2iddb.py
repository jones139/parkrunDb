#!/usr/bin/python
import json

f = open('partlist.json','r')
partList = json.load(f)
f.close()

iddb = []
for part in partList:
    if part['id'] == 'unknown':
        print 'skipping unknown participant %s' % part['name']
    else:
        iddb.append({'id':part['id'], 'name':part['name']})
        

print "Writting iddb.json"
f = open('iddb.json','w')
json.dump(iddb,f,indent=4, separators=(',', ': '))
f.close()

        
