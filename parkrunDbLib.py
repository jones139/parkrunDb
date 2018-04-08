#!/usr/bin/python
"""
Library to handle parkrun data in an sqlite database
"""
import sqlite3
import json
import dateutil.parser
import datetime, time

class parkrunDbLib:
    def __init__(self,dbFname, idFname = None, Debug=True):
        """ Initialise the library using database file named dbFname.
        Optional idFname parameter specifies a file containing a JSON
        array of {id, name} objects to use as a lookup for unknown volunteer
        runners.
        FIXME:  Handle file not found errors, and incorreclty initialised
        database files - this will just crash!
        """
        self.DEBUG = Debug
        if (self.DEBUG): print "parkrunDbLib.__init()__: fname=%s" % dbFname
        self.conn = sqlite3.connect(dbFname)
        self.idFname = idFname
        self.iddb = None  # We cache the contents of idFname the first time it is used.

    ########################################
    # Utilities
    def dateStr2ts(self,dateStr):
        """ Convert a string date dd/mm/yyyy to unix timestamp """
        dt = dateutil.parser.parse(dateStr,dayfirst=True)
        ts = time.mktime(dt.timetuple())
        return ts

    def ts2dateStr(self,ts):
        """ Convert a unix timestamp to dd/mm/yyyy string
        """
        print type(ts),ts
        return datetime.datetime.fromtimestamp(ts).strftime('%d/%m/%Y')

    #########################################
    # Initialise database
    def initialiseDb(self,initFname):
        """ Initialise the database with the sql scriptfile initFname.
        **** This is likely to wipe all the data in the database, so use
        carefully!!!! ****
        """
        print "Initialising Database with file %s" % initFname
        f = open(initFname,"r")
        sqlStr = f.read()
        f.close()
        cur = self.conn.executescript(sqlStr)
        self.conn.commit()
        

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
        sqlStr = ("insert into parkruns "
                  "(parkrunRef,name,created,modified) "
                  "values(?, ? ,date('now'),date('now'));")
        if (self.DEBUG): print type(prName), prName
        if (self.DEBUG): print sqlStr
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
        


    def getEventId(self,parkrunId,dateVal):
        """ Check the database to see if we already have an event for parkrunId
        on date DateVal.  DateVal must be a unix timestamp
        If so, return the event Id, or -1 if not.
        """
        #Check if the event exists, if not create it.
        sqlStr = "select id from events where parkrunId=? and dateVal=?"
        sqlParams = (parkrunId,dateVal,)
        if (self.DEBUG): print "sqlStr=%s." % sqlStr
        if (self.DEBUG): print sqlParams
        cur = self.conn.execute(sqlStr,sqlParams)
        rows = cur.fetchall()
        if (len(rows)>0): # event already exists
            eventId = rows[0][0]
            if (self.DEBUG): print "Found event id %d" % (eventId)
        else:
            eventId = -1
        return eventId
    
    def getEventIdFromEventNo(self,parkrunId,eventNo):
        """ Check the database to see if we already have an event for parkrunId
        with number eventNo. 
        If so, return the event Id, or -1 if not.
        """
        sqlStr = "select id from events where parkrunId=? and eventNo=?"
        sqlParams = (parkrunId,eventNo,)
        if (self.DEBUG): print "sqlStr=%s." % sqlStr
        if (self.DEBUG): print sqlParams
        cur = self.conn.execute(sqlStr,sqlParams)
        rows = cur.fetchall()
        if (len(rows)>0): # event already exists
            eventId = rows[0][0]
            if (self.DEBUG): print "Found event id %d" % (eventId)
        else:
            eventId = -1
        return eventId


    def addEvent(self,eventNo, parkrunId, dateVal):
        """ Create event number eventNo for parkrun parkrunId on date dateVal.
        DateVal must be a unix timestamp
        Returns the new event ID
        """
        # create an event
        sqlStr = "insert into events (eventNo, parkrunId, dateVal, created," \
        "modified) " \
        " values (?,?,?,date('now'),date('now'))"
        sqlParams = (eventNo,
                     parkrunId,
                     dateVal,
        )
        if(self.DEBUG): print "addEvent - sqlStr =%s." % sqlStr 
        if(self.DEBUG): print sqlParams
        cur = self.conn.execute(sqlStr,
                                sqlParams
        )
        eventId = cur.lastrowid
        self.conn.commit()
        if (self.DEBUG): print "addEvent - created event %d for date %d (%s)" % (eventId,dateVal,self.ts2dateStr(dateVal))
        return eventId

    #########################################
    # Runners
    def getRunnerId(self,runnerNo):
        """ Look in the runners table to see if runnerNo exists.  Return -1
        if not.
        """
        sqlStr = "select id from runners where runnerNo=?"
        cur = self.conn.execute(sqlStr,(runnerNo,))
        rows = cur.fetchall()
        if (len(rows)>0): # event already exists
            runnerId = rows[0][0]
            if (self.DEBUG): print "Found runner id %d" % (runnerId)
        else:
            runnerId = -1
        return runnerId

    def getRunnerIdFromName(self,nameStr):
        """ Look up the runner ID in the runners table to return the runner Id.
        if it is not found, the self.idFname file is used to attempt to look it
        up, and then add it to the main database.
        Returns the runner ID or -1 if not found.
        """
        sqlStr = "select id from runners where name=?"
        sqlParams=(nameStr,)
        cur = self.conn.execute(sqlStr,sqlParams)
        rows = cur.fetchall()
        if (len(rows)>0): # event already exists
            runnerId = rows[0][0]
            if (self.DEBUG): print "getRunnerIdFromName() Found runner id %d in database" % (runnerId)
        elif (self.idFname != None):
            # Attempt to look up the name in idFname file
            # idFname should contain a json array of {id,name} objects.
            if (self.DEBUG): print "getRunnerIdFromName(): Attempting to use external runner id database."
            if (self.iddb == None):
                f = open(self.idFname,'r')
                self.iddb = json.load(f)
                f.close()
            runnerId = -1
            for idrec in self.iddb:
                if idrec['name'] == nameStr and idrec['id']!= 'unknown':
                    runnerId = int(idrec['id'])
                    if (self.DEBUG): print "getRunnerIdFromName() Found runner id %d in id database" % (runnerId)
        else:
            if (self.DEBUG): print "getRunnerIdFromName() failed to find runner %s" % nameStr
            runnerId = -1
        return runnerId
        
    
    def addRunner(self,runnerNo, nameStr, clubStr, genderStr):
        """ Create runner record for runnerId
        Returns the new runner ID
        """
        # create a runner
        sqlStr = "insert into runners (runnerNo, name, club, gender, created," \
        "modified) " \
        " values (?,?,?,?,date('now'), date('now'))"
        sqlParams = (runnerNo,nameStr,clubStr,genderStr,)
        if(self.DEBUG): print "createRunner - sqlStr =%s." % sqlStr 
        if(self.DEBUG): print sqlParams
        cur = self.conn.execute(sqlStr, sqlParams)

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
        
    def addRun(self,eventId, runnerId, roleId, runTime,ageCat,ageGrade,finishPos,genderPos,note):
        """ Create run for runner runnerId at event eventId doing role roleID
        in runTime seconds.
        Returns the new run ID
        """
        # create an event
        sqlStr = "insert into runs (eventId, runnerId, roleId, finishPos, genderPos, ageCat,ageGrade,note,runTime, created," \
        "modified) " \
        " values (?,?,?,?,?,?,?,?,?,date('now'),date('now'))"
        sqlParams = (eventId,runnerId, roleId,  finishPos,genderPos,
                     ageCat,ageGrade,note,runTime,)
        if(self.DEBUG): print "addRun - sqlStr =%s." % sqlStr 
        if(self.DEBUG): print sqlParams
        cur = self.conn.execute(sqlStr,sqlParams)
        runId = cur.lastrowid
        self.conn.commit()
        if (self.DEBUG): print "createRun - created run %d" % (runId)
        return runId

    #############################
    # Queries
    def getEventHistory(self,parkrunStr,startTs,endTs):
        """ returns a cursor pointing to the event history for the given parkrun
        between timestamps startTs and endTs
        """
        prId = self.getParkrunId(parkrunStr)
        if (prId==-1):
            return None
        else:
            #strftime('%d-%m-%Y', (date/1000)) as_string
            sqlStr = ("select eventNo, id, dateVal, "
                      "strftime('%d-%m-%Y',datetime(dateVal, 'unixepoch',"
                      "'localtime')) as dateStr, "
                      "(select count(id) from runs "
                      "    where runs.eventId=events.Id and runs.roleId=0) "
                      "    as runners, "
                      "(select count(id) from runs "
                      "    where runs.eventId=events.Id and runs.roleId=1) "
                      "    as volunteers "
                      "from events "
                      "where parkrunId = ? "
                      " and dateVal>=? and dateVal<=? "
                      "order by dateVal desc"
                      )
            sqlParams = (prId,startTs,endTs)
            cur = self.conn.execute(sqlStr,sqlParams)
            rows = cur.fetchall()
            return rows

    def getEventResults(self,parkrunStr,eventNo):
        """ returns set of rows containing results for the given parkrun event.
        """
        prId = self.getParkrunId(parkrunStr)
        eventId = self.getEventIdFromEventNo(prId,eventNo)
        print ("getEventResults - parkrunStr=%s (id=%d), eventNo=%d (id=%d)"
               % (parkrunStr,prId, eventNo, eventId))
        if (prId==-1 | eventId==-1):
            return None
        else:
            sqlStr = ("select finishPos, runners.name, runTime "
                      "from runs, runners "
                      "where runs.eventId = ? and runs.runnerId=runners.Id"
                      " order by runs.finishPos asc"
                      )
            sqlParams = (eventId,)
            cur = self.conn.execute(sqlStr,sqlParams)
            rows = cur.fetchall()
            return rows

        
if __name__ == "__main__":
    db = parkrunDbLib("parkrun.db")
    print "Parkruns: ", db.getParkruns()
    print "Parkrun 0 = ", db.getParkrunName(0)
    print "Parkrun 0 events= ", db.getEvents(0)
    print "Parkrun 0 event on 01/01/2018 is event no ", db.getEventId(0,"01/01/2018")
    print db.getEventId(0,"01/01/2018")
    #print db.getEventId(0,"01/01/2018",True)
    #print db.getEventId(0,"01/01/2018")
