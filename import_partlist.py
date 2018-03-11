#!/usr/bin/python

import json
import sqlite3
from parkrunDbLib import parkrunDbLib

DEBUG = True
dbFname = "parkrun.db"


def addRun(idRec,db):
    if (DEBUG): print idRec
    runnerId = int(idRec['id'])
    nameStr = idRec['name']
    runDateStr = idRec['date']
    if (idRec['activity'] == 'run'):
        roleId = 0
        clubStr = idRec['club']
        genderStr = idRec['gender']
        posVal = idRec['pos']
        genderPosVal = idRec['genderPos']
        ageCatStr = idRec['ageCat']
        noteStr = idRec['note']
        runTime = idRec['runTime']
    else:
        roleId = 1
        clubStr = ""
        genderStr = ""
        posVal = -1
        genderPosVal = -1
        ageCatStr = ""
        noteStr = ""
        runTime = -1

    eventId = db.getEventId(0,runDateStr)
    if (eventId==-1):
        eventId = db.createEvent(0,0,runDateStr)
    print "eventId=%d" % (eventId)

    runnerId_db = db.getRunnerId(runnerId)
    if (runnerId_db==-1):
        runnerId_db = db.createRunner(runnerId,nameStr,clubStr,genderStr)
    print "runnerId_db = %d" % (runnerId_db)

    runId = db.getRunId(eventId, runnerId, roleId)
    if (runId==-1):
        runId = db.createRun(eventId, runnerId, roleId, runTime)
        print "Added runId %d" % runId
    

db = parkrunDbLib("parkrun.db")
f = open('partlist.json','r')
iddb = json.load(f)
f.close()

for idrec in iddb:
    #print part['name']
    addRun(idrec,db)


