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
    def getRunner(self,runnerId):
        """return the data for runner id runnerId. """
        sqlStr = "select runnerNo, name, club, gender from runners where id=?"
        sqlParams=(runnerId,)
        cur = self.conn.execute(sqlStr,sqlParams)
        rows = cur.fetchall()
        if (len(rows)>0):
            return rows[0]
        else:
            return None
        
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

    def getRunnerNoFromName(self,nameStr):
        """ Look up the runner Name in the runners table to return the runner Number.
        if it is not found, the self.idFname file is used to attempt to look it
        up, and then add it to the main database.
        Returns the runner Number (=parkrun barcode no) or -1 if not found.
        """
        sqlStr = "select runnerNo from runners where name=?"
        sqlParams=(nameStr,)
        cur = self.conn.execute(sqlStr,sqlParams)
        rows = cur.fetchall()
        if (len(rows)>0): # event already exists
            runnerNo = rows[0][0]
            if (self.DEBUG): print "getRunnerNoFromName() Found runner No %d in database" % (runnerNo)
        elif (self.idFname != None):
            # Attempt to look up the name in idFname file
            # idFname should contain a json array of {id,name} objects.
            if (self.DEBUG): print "getRunnerNoFromName(): Attempting to use external runner id database."
            if (self.iddb == None):
                f = open(self.idFname,'r')
                self.iddb = json.load(f)
                f.close()
            runnerNo = -1
            for idrec in self.iddb:
                if idrec['name'] == nameStr and idrec['id']!= 'unknown':
                    runnerNo = int(idrec['id'])
                    if (self.DEBUG): print "getRunnerNoFromName() Found runner No %d in id database" % (runnerNo)
        else:
            if (self.DEBUG): print "getRunnerNoFromName() failed to find runner %s" % nameStr
            runnerNo = -1
        return runnerNo
        
    
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

    def updateRunner(self,runnerId, runnerNo, nameStr, clubStr, genderStr):
        """ update runner record for runnerId
        Returns the runnerId
        """
        # update runner
        sqlStr = ("update runners set"
                  "  runnerNo = ?, "
                  "  name = ?, "
                  "  club = ?, "
                  "  gender = ?,"
                  "  modified = date('now') "
                  " where id = ?"
                  )
        sqlParams = (runnerNo,nameStr,clubStr,genderStr,runnerId,)
        if(self.DEBUG): print "updateRunner - sqlStr =%s." % sqlStr 
        if(self.DEBUG): print sqlParams
        cur = self.conn.execute(sqlStr, sqlParams)
        self.conn.commit()
        if (self.DEBUG): print "updateRunner - updated %d rows" % (cur.rowcount)
        return cur.rowcount

    
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

    def getEventsListSql(self,prId,startTs,endTs):
        """ Returns (sql,paramDict) which is the 
        SQL query to return the list of event IDs for parkrun prId
        beween the specified dates, and a dictionary of the parameters.
        """
        sqlStr = "select id from events where parkrunId=:parkrunId and dateVal>=:startTs and dateVal<=:endTs order by dateVal"
        paramDict = {"parkrunId":prId, "startTs":startTs,"endTs":endTs}
        return sqlStr,paramDict

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
                      ", "
                      "(select count(id) from runs "
                      "    where runs.eventId=events.Id and runs.note='New PB!') "
                      "    as PBcount "
                      ", "
                      "(select count(id) from runs "
                      "    where runs.eventId=events.Id and runs.note='First Timer!') "
                      "    as FirstTimecount "
                      "from events "
                      "where parkrunId = ? "
                      " and dateVal>=? and dateVal<=? "
                      "order by dateVal desc"
                      )
            sqlParams = (prId,startTs,endTs)
            cur = self.conn.execute(sqlStr,sqlParams)
            rows = cur.fetchall()
            return rows

    def getEventAttendanceSummary(self,parkrunStr,startTs,endTs):
        """ returns a cursor pointing to the event attendance summary
        (annual number of runs)
        between timestamps startTs and endTs
        """
        prId = self.getParkrunId(parkrunStr)
        if (prId==-1):
            return None
        else:
            #strftime('%d-%m-%Y', (date/1000)) as_string
            sqlStr = (
                "select yearStr, count(eventNo), sum(runners), sum(volunteers), "
                "sum(PBcount), sum(FirstTimeCount) from "
                "(select eventNo, id, dateVal, "
                "strftime('%Y',datetime(dateVal, 'unixepoch',"
                "'localtime')) as yearStr, "
                "strftime('%d-%m-%Y',datetime(dateVal, 'unixepoch',"
                "'localtime')) as dateStr, "
                "(select count(id) from runs "
                "    where runs.eventId=events.Id and runs.roleId=0) "
                "    as runners, "
                "(select count(id) from runs "
                "    where runs.eventId=events.Id and runs.roleId=1) "
                "    as volunteers "
                ", "
                "(select count(id) from runs "
                "    where runs.eventId=events.Id and runs.note='New PB!') "
                "    as PBcount "
                ", "
                "(select count(id) from runs "
                "    where runs.eventId=events.Id and runs.note='First Timer!') "
                "    as FirstTimecount "
                "from events "
                "where parkrunId = ? "
                " and dateVal>=? and dateVal<=? "
                "order by dateVal desc) "
                "group by yearStr"
            )

            sqlParams = (prId,startTs,endTs)
            print("sqlStr=%s" % sqlStr)
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

    def getVolStats(self,parkrunStr,startTs,endTs,thresh,limit,orderBy):
        """ returns set of rows containing 
        volunteering statistics for the given parkrun between the specified
        dates.
        Only runners who have participated in at least thresh number of events
        are included.
        Returns 'limit' number of rows
        OrderBy is an integer 1 = total activities, 2=runs, 3= volunteers
        """
        prId = self.getParkrunId(parkrunStr)
        print ("getVolStats - parkrunStr=%s (id=%d)"
               % (parkrunStr,prId))
        if (prId==-1 ):
            print "ERROR - Parkrun %s not found" % parkrunStr
            return None
        else:
            # Get the SQL string to give us a list of event IDs to use
            # in queries.
            selEventsSql,sqlParams = self.getEventsListSql(prId,startTs,endTs)

            # calculate number of runs for each runner
            runsSqlStr = (
                " select name, runnerNo, count(runs.id) as nr, "
                "       sum(runs.runTime) as tr"
                "  from runners, runs "
                "    where runs.eventId in "
                "      ("+selEventsSql+") "
                "    and runs.roleId = 0 "
                "   "
                " and runs.runnerId=runners.Id "
                " group by runnerId"
                " order by count(runs.id) desc"
            )

            # calculate number of volunteerings for each runner
            # set time on feet to zero for volunteers, because otherwise
            # we were getting the top volunteers winning time on feet too.
            volsSqlStr = (
                " select name, runnerNo, count(runs.id) as nv, "
                " 0 as tv"
                "  from runners, runs "
                "    where runs.eventId in "
                "      ("+selEventsSql+") "
                "    and runs.roleId = 1 "
                "   "
                " and runs.runnerId=runners.Id "
                " group by runnerId"
                " order by count(runs.id) desc "
            )

            orderByStr = ""
            if (orderBy==1):
                orderByStr = " order by total desc "
            elif (orderBy==2):
                orderByStr = " order by nr desc "
            elif (orderBy==3):
                orderByStr = " order by nv desc "
            elif (orderBy==4):
                orderByStr = " order by timeOnFeet desc "
            
            # We want all runners who have:
            #    - ran but not volunteered
            #    - volunteered but not ran
            #    - volunteered and ran
            # so we have to union together two queries to make sure we get
            # them all.
            # The 'coalesce' statements are to force Null to be returned as zero
            #     so that calculations work.
            sqlStr = (
                "select r.name, r.runnerNo, coalesce(r.nr,0) as nr, "
                "               coalesce(v.nv,0) as nv, "
                "               coalesce(r.nr,0) + coalesce(v.nv,0) as total, "
                "               coalesce(r.tr,0), coalesce(v.tv,0), "
                "               coalesce(r.tr,0) + coalesce(v.tv,0) as timeOnFeet "
                " from "
                " (" +runsSqlStr + ") r"
                "    left join "
                "       (" +volsSqlStr + ") v"
                "           on r.runnerNo = v.runnerNo"
                "    where total >= :thresh "
                " union  "
                "select v.name, v.runnerNo, coalesce(r.nr,0) as nr, "
                "              coalesce(v.nv,0) as nv, "
                "              coalesce(r.nr,0) + coalesce(v.nv,0) as total, "
                "               coalesce(r.tr,0), coalesce(v.tv,0), "
                "               coalesce(r.tr,0) + coalesce(v.tv,0) as timeOnFeet "
                " from "
                " (" +volsSqlStr + ") v"
                "    left outer join "
                "       (" +runsSqlStr + ") r"
                "           on v.runnerNo = r.runnerNo"
                " where total >= :thresh "
                + orderByStr +
                " limit :limit"
            )
            sqlParams['thresh']=thresh
            sqlParams['limit']=limit
            
            if (self.DEBUG): print sqlStr,sqlParams
            cur = self.conn.execute(sqlStr,sqlParams)
            rows = cur.fetchall()
            return rows

    def getRunnerList(self,parkrunStr,startTs,endTs,thresh,limit):
        """ returns a list of runnerIds 
        of runners for the given parkrun between the specified
        dates.
        Only runners who have participated in at least thresh number of events
        are included.
        Returns 'limit' number of rows
        """
        prId = self.getParkrunId(parkrunStr)
        if (self.DEBUG): print ("getRunnerList - parkrunStr=%s (id=%d)"
                                % (parkrunStr,prId))
        if (prId==-1 ):
            print "ERROR - Parkrun %s not found" % parkrunStr
            return None
        else:
            # Get the SQL string to give us a list of event IDs to use
            # in queries.
            selEventsSql,sqlParams = self.getEventsListSql(prId,startTs,endTs)

            # calculate number of runs for each runner
            sqlStr = (
                " select runners.id, runners.name, runners.runnerNo, "
                "       count(runs.id) as nr, "
                "       sum(runs.runTime) as tr"
                "  from runners, runs "
                "    where runs.eventId in "
                "      ("+selEventsSql+") "
                "    and runs.roleId = 0 "
                "   "
                " and runs.runnerId=runners.Id "
                " group by runnerId"
                " having count(runs.id)>=:thresh "
                " order by count(runs.id) desc"
                " limit :limit "
            )

            sqlParams['thresh']=thresh
            sqlParams['limit']=limit
            
            if (self.DEBUG): print sqlStr,sqlParams
            cur = self.conn.execute(sqlStr,sqlParams)
            rows = cur.fetchall()
            return rows

    def getRunnerHistory(self,runnerId, parkrunStr,startTs,endTs):
        """ returns the run history for runner id runnerId
        for the given parkrun between the specified dates
        """
        prId = self.getParkrunId(parkrunStr)
        if (self.DEBUG): print ("getRunnerList - parkrunStr=%s (id=%d)"
                                % (parkrunStr,prId))
        if (prId==-1 ):
            print "ERROR - Parkrun %s not found" % parkrunStr
            return None
        else:
            # Get the SQL string to give us a list of event IDs to use
            # in queries.
            selEventsSql,sqlParams = self.getEventsListSql(prId,startTs,endTs)

            if (self.DEBUG):
                print "EVENTS LIST TO PROCESS: ",selEventsSql,sqlParams
                cur = self.conn.execute(selEventsSql,sqlParams)
                rows = cur.fetchall()
                for r in rows:
                    print r
                
            
            # calculate number of runs for each runner
            sqlStr = (
                " select runs.eventId, events.dateVal, "
                      "strftime('%d-%m-%Y',datetime(dateVal, 'unixepoch',"
                      "'localtime')) as dateStr, "
                "        runs.runnerId, runs.finishPos, "
                "        runs.genderPos, "
                "        runs.ageGrade, runs.runTime "
                "  from events, runs "
                "    where runs.eventId in "
                "      ("+selEventsSql+") "
                "    and events.id=runs.eventId "
                "    and runs.roleId = 0 "
                "    and runs.runnerId = :runnerId "
                "   "
                " order by events.dateVal asc"
            )

            sqlParams['runnerId']=runnerId
            
            if (self.DEBUG): print sqlStr,sqlParams
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
