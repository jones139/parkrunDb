#!/usr/bin/python

import json


f = open('partlist.json','r')
partList = json.load(f)
f.close()


def getPartIndex(id,partStats):
    for i in range (0,len(partStats)):
        part = partStats[i]
        if part['id'] == id:
            return i
    partStats.append({'id':id, 'name':'', 'nRun':0,'nVol':0})
    return len(partStats)-1

# Count number of volunteering and running activities.
partStats = []
nRunActivities = 0
nVolActivities = 0
for part in partList:
    i = getPartIndex(part['id'],partStats)
    if part['activity'] == 'run':
        partStats[i]['nRun'] += 1
        nRunActivities += 1
    else:
        partStats[i]['nVol'] += 1
        nVolActivities += 1
    partStats[i]['name'] = part['name']

print "Total Run Activities = %d,  Total Vol Activities= %d.  Ratio = %4.1f%%" % \
    (nRunActivities,nVolActivities,100.0*nVolActivities/nRunActivities)

for part in partStats:
    if part['nRun'] >0:
        part['ratio'] = 100.0*part['nVol'] / part['nRun']
    else:
        part['ratio'] = 1000.

#print json.dumps(partStats,indent=2)


print "writing partitipants statistics..."        
f = open('partstats.json','w')
json.dump(partStats,f,indent=2, separators=(',', ': '))
f.close()
