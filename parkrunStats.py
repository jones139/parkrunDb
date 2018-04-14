#!/usr/bin/python
""" Calculates various statistics and produces output from parkrun database.
"""
from parkrunDbLib import parkrunDbLib
import argparse
import os

def getEventHistory(db,parkrunStr,startTs,endTs):
    """ Produce an event history summary """
    rows = db.getEventHistory(parkrunStr,startTs,endTs)

    for row in rows:
        print row


def getEventResults(db,parkrunStr,eventNo):
    """ Produce an event results summary """
    rows = db.getEventResults(parkrunStr,eventNo)
    for row in rows:
        print row

def getVolStats(db,parkrunStr,startTs,endTs,thresh,limit):
    """ produce volunteer statistics for each participant
    """
    rows = db.getVolStats(parkrunStr,startTs,endTs,thresh,limit)
    for row in rows:
        print row
    
        
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("command", help="command to execute")
    ap.add_argument("-db", "--database", help="Filename of Database to use (Defaults to ./parkrun.db")
    ap.add_argument("-pr", "--parkrun", help="name of parkrun to process (defaults to 'Hartlepool'")
    ap.add_argument("-ev", "--event", help="event number to process (defaults to '1'")
    ap.add_argument("-th", "--thresh", help="threshold number of runs to include in statistics - runners with less than this number of runs are excluded (defaults to '1')")
    ap.add_argument("-lim", "--limit", help="Number of rows of statistics returned (defaults to '10')")
    ap.add_argument("-sd", "--startDate", help="earliest date to process (defaults to '01/01/2014'")
    ap.add_argument("-ed", "--endDate", help="latest date to process (defaults to '01/01/2024'")

    ap.add_argument("-v", "--verbose",
                    help="produce verbose output for debugging",
                    action="count")
    args = ap.parse_args()

    verbose = args.verbose
    if (verbose): print args


    cmdStr = args.command

    if (args.database!=None):
        dbFname = args.database
    else:
        dbFname = "./parkrun.db"
    db = parkrunDbLib(dbFname)

    if (args.parkrun!=None):
        parkrunStr = args.parkrun
    else:
        parkrunStr = "Hartlepool"

    if (args.event!=None):
        eventNo = int(args.event)
    else:
        eventNo = 1

    if (args.thresh!=None):
        thresh = int(args.thresh)
    else:
        thresh = 1

    if (args.limit!=None):
        limit = int(args.limit)
    else:
        limit = 10

    if (args.startDate!=None):
        startTs = db.dateStr2ts(args.startDate)
    else:
        startTs = db.dateStr2ts("01/01/2014")

    if (args.endDate!=None):
        endTs = db.dateStr2ts(args.endDate)
    else:
        endTs = db.dateStr2ts("01/01/2024")

    if (verbose): print "startTs = %d (%s)" % (startTs,db.ts2dateStr(startTs))
    if (verbose): print "endTs = %d (%s)" % (endTs,db.ts2dateStr(endTs))
        

    if (cmdStr=="history"):
        getEventHistory(db,parkrunStr,startTs,endTs)
    elif (cmdStr=="results"):
        getEventResults(db,parkrunStr,eventNo)
    elif (cmdStr=="volstats"):
        getVolStats(db,parkrunStr,startTs,endTs,thresh,limit)
    else:
        print "ERROR: Command %s not recognised" % cmdStr


