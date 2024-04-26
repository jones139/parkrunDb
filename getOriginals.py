#!/usr/bin/env python

''' Get a list of attendees at parkrun no 1 who are still regular attendees
'''
verbose = True
REGFRAC = 0.25  # Define a 'regular' as someone who attends at least 25% of parkruns
dbFname = 'parkrun.db'
parkrunStr = 'Hartlepool'

from parkrunDbLib import parkrunDbLib

db = parkrunDbLib(dbFname,Debug=(verbose>2))

startTs = db.dateStr2ts("01/05/2023")
endTs = db.dateStr2ts("01/05/2024")

regLim = 52*REGFRAC

if (verbose): print("startTs = %d (%s)" % (startTs,db.ts2dateStr(startTs)))
if (verbose): print("endTs = %d (%s)" % (endTs,db.ts2dateStr(endTs)))

# Sort by total number of activities (orderBy=1)
regularRows = db.getVolStats(parkrunStr,startTs,endTs,1,999,1)

n=0
for row in regularRows:
    if (row[1]!=0):   # Ignore 'Unknown'
        if (row[4]>regLim):
            print(n, row[0], row[2], row[3], row[4])
            n+= 1


startTs = db.dateStr2ts("25/04/2014")
endTs = db.dateStr2ts("27/04/2014")
originalRows = db.getVolStats(parkrunStr,startTs,endTs,1,999,1)
print("Originals who attended in last year")
n=0
for row in originalRows:
    for regRow in regularRows:
        if (row[1] == regRow[1]):
            print(n, row[0], regRow[4])
            n+=1


print("Originals who are regulars")
n=0
for row in originalRows:
    for regRow in regularRows:
        if (row[1] == regRow[1] and row[1]!=0):
            if (regRow[4]>regLim):
                print(n, row[0], regRow[4])
                n+=1
