#!/usr/bin/python

import sqlite3
import json

class parkrunDbLib:
    DEBUG = True
    def __init__(self,dbFname):
        if (self.DEBUG): print "parkrunDbLib.__init()__: fname=%s" % dbFname
        self.conn = sqlite3.connect(dbFname)

    #########################################
    # Parkruns
    def getParkruns(self):
        sqlStr = "select id, parkrunRef, name from parkruns"
        cur = self.conn.execute(sqlStr,())
        rows = cur.fetchall()
        parkruns = []
        for row in rows:
            parkruns.append({'id':row[0], 'parkrunRef':row[1], 'name':row[2]})
        return parkruns
        
    def getParkrunName(self,id):
        sqlStr = "select name from parkruns where id=?"
        cur = self.conn.execute(sqlStr,(id,))
        rows = cur.fetchall()
        if (len(rows)>0):
            parkrunName = rows[0][0]
        else:
            parkrunName = "unknown"
        return parkrunName
        
    def getParkrunId(self,prName):
        sqlStr = "select id from parkruns where name=?"
        cur = self.conn.execute(sqlStr,(prName,))
        rows = cur.fetchall()
        if (len(rows)>0):
            parkrunId = rows[0][0]
        else:
            parkrunId = -1
        return parkrunId

    def addParkrun(self,prName):
        sqlStr = "insert into parkruns (parkrunRef,name,created,modified) values(?, ? ,date('now'),date('now'));"
        print type(prName), prName
        cur = self.conn.execute(sqlStr,(prName,prName,))
        prId = cur.lastrowid
        self.conn.commit()
        if (self.DEBUG): print "addParkrun - created parkrun %s with ID %d" % (prName,prId)
        return prId
    
    #########################################
    # Events
    def getEvents(self,parkrunId,dateMin='1970-01-01',dateMax='2100-01-01'):
        sqlStr = "select date, parkruns.name, eventNo from events, parkruns where (parkruns.id=events.parkrunId and events.date>=date(?) and events.date<=date(?)) order by events.date"
        cur = self.conn.execute(sqlStr,(dateMin,dateMax,))
        rows = cur.fetchall()
        parkruns = []
        for row in rows:
            parkruns.append({'date':row[0], 'name':row[1], 'eventNo':row[2]})
        return parkruns
        


    def getEventId(self,parkrunId,dateStr):
        """ Check the database to see if we already have an event for parkrunId
        on date DateStr.  If so, return the event Id, or -1 if not.
        """
        #Check if the event exists, if not create it.
        sqlStr = "select id from events where parkrunId=? and date=?"
        cur = self.conn.execute(sqlStr,(0,dateStr,))
        rows = cur.fetchall()
        if (len(rows)>0): # event already exists
            eventId = rows[0][0]
            if (self.DEBUG): print "Found event id %d" % (eventId)
        else:
            eventId = -1
        return eventId
    
    def createEvent(self,eventNo, parkrunId, date):
        """ Create event number eventNo for parkrun parkrunId on date date.
        Returns the new event ID
        """
        # create an event
        sqlStr = "insert into events (eventNo, parkrunId, date, created," \
        "modified) " \
        " values (?,?,?,?,?)"
        if(self.DEBUG): print "getEventId - sqlStr =%s." % sqlStr 
        cur = self.conn.execute(sqlStr,
                                (eventNo,
                                 parkrunId,
                                 date,
                                 "date(now)",
                                 "date(now)",)
        )
        eventId = cur.lastrowid
        self.conn.commit()
        if (self.DEBUG): print "getEventId - created event %d for date %s" % (eventId,date)
        return eventId

    #########################################
    # Runners
    def getRunnerId(self,runnerId):
        """ Look in the runners table to see if runnerId exists.  Return -1
        if not.
        """
        sqlStr = "select id from runners where id=?"
        cur = self.conn.execute(sqlStr,(runnerId,))
        rows = cur.fetchall()
        if (len(rows)>0): # event already exists
            runnerId = rows[0][0]
            if (self.DEBUG): print "Found runner id %d" % (runnerId)
        else:
            runnerId = -1
        return runnerId
        
    def createRunner(self,runnerId, nameStr, clubStr, genderStr):
        """ Create runner record for runnerId
        Returns the new runner ID
        """
        # create a runner
        sqlStr = "insert into runners (id, name, club, gender, created," \
        "modified) " \
        " values (?,?,?,?,?,?)"
        if(self.DEBUG): print "createRunner - sqlStr =%s." % sqlStr 
        cur = self.conn.execute(sqlStr,
                                (runnerId,
                                 nameStr,
                                 clubStr,
                                 genderStr,
                                 "date(now)",
                                 "date(now)",)
        )
        runnerId = cur.lastrowid
        self.conn.commit()
        if (self.DEBUG): print "createRunner - created runner %d" % (runnerId)
        return runnerId

    #############################################
    # Runs
    def getRunId(self,eventId,runnerId, roleId):
        """ Check the database to see if we already have runner runnerId
        taking part as role RoleId for event eventId.
        If so, return the run Id, or -1 if not.
        """
        sqlStr = "select id from runs where eventId=? and runnerId=? and roleId=?"
        cur = self.conn.execute(sqlStr,(eventId,runnerId,roleId,))
        rows = cur.fetchall()
        if (len(rows)>0): # event already exists
            runId = rows[0][0]
            if (self.DEBUG): print "Found event id %d" % (eventId)
        else:
            runId = -1
        return runId
        
    def createRun(self,eventId, runnerId, roleId, runTime):
        """ Create run for runner runnerId at event eventId doing role roleID
        in runTime seconds.
        Returns the new run ID
        """
        # create an event
        sqlStr = "insert into runs (eventId, runnerId, roleId, runTime, created," \
        "modified) " \
        " values (?,?,?,?,?,?)"
        if(self.DEBUG): print "createRun - sqlStr =%s." % sqlStr 
        cur = self.conn.execute(sqlStr,
                                (eventId,
                                 runnerId,
                                 roleId,
                                 runTime,
                                 "date(now)",
                                 "date(now)",)
        )
        runId = cur.lastrowid
        self.conn.commit()
        if (self.DEBUG): print "createRun - created run %d" % (runId)
        return runId
    

    
db = parkrunDbLib("parkrun.db")
print "Parkruns: ", db.getParkruns()
print "Parkrun 0 = ", db.getParkrunName(0)
print "Parkrun 0 events= ", db.getEvents(0)
print "Parkrun 0 event on 01/01/2018 is event no ", db.getEventId(0,"01/01/2018")
print db.getEventId(0,"01/01/2018")
#print db.getEventId(0,"01/01/2018",True)
#print db.getEventId(0,"01/01/2018")
