#!/usr/bin/python
""" Calculates various statistics and produces output from parkrun database.
"""
from parkrunDbLib import parkrunDbLib
import argparse
import os
import math

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

def getVolStats(db,parkrunStr,startTs,endTs,thresh,limit,orderBy):
    """ produce volunteer statistics for each participant
    """
    rows = db.getVolStats(parkrunStr,startTs,endTs,thresh,limit,orderBy)
    for row in rows:
        print row

def calcMeanStDev(tArr,sigTh):
    """ Calculate the mean and standard deviation of the data in tArr,
    excluding outliers that are more than sigTh standard deviations from the mean.
    """
    dataOk = False

    # we iterate until all the data lies within sigTh
    while not dataOk:
        totT = 0
        nT = 0
        avT = 0.
        stDev = 0.
        # Calculate Mean
        for t in tArr:
            #print t
            totT = totT + t
            nT = nT + 1
        avT = totT/nT
        # calculate standard deviation
        for t in tArr:
            stDev = stDev + (t-avT)*(t-avT)
        stDev = math.sqrt(stDev/(nT-1))

        # Check if all data lies within standard eviation limit sigTh,
        # and remove any outliers from the data.
        #print "Checking...."
        dataOk = True
        for t in tArr:
            #print "%f, %f, %f, %f, %f" % (t, avT, stDev, abs(t-avT)/stDev, (sigTh*stDev))
            if (abs(t-avT)>(sigTh*stDev)):
                #print "   Removing %f" % t
                tArr.remove(t)
                dataOk=False
    return (nT,avT,stDev)

def getRunnerStats(db,parkrunStr,startTs,endTs,thresh,limit):
    print "getRunnerStats()"
    rows = db.getRunnerList(parkrunStr,startTs,endTs,thresh,10000)
    resultsArr = []
    for row in rows:
        #print row
        if (row[1]=="Unknown"):
            print "Ignoring the Unknown Runner...."
        else:
            runnerId = row[0]
            runnerHist = db.getRunnerHistory(runnerId,parkrunStr,startTs,endTs)
            timesArr = []
            for run in runnerHist:
                #print run
                timesArr.append(run[7])
            (nT,avT,stDevT) = calcMeanStDev(timesArr,3)
            #print "%s, %d runs, Average Time=%f, stDev=%f" \
            #    % (row[1],nT,avT,stDevT)
            resultsArr.append((row[1],nT,avT,stDevT))
    # Sort into standard deviation order (element 3 in each row)
    resultsArr.sort(key=lambda x: x[3], reverse=False)
    print "Sorted Results..."
    for r in resultsArr[0:limit]:
        print r
            
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("command", help="command to execute")
    ap.add_argument("-db", "--database", help="Filename of Database to use (Defaults to ./parkrun.db")
    ap.add_argument("-pr", "--parkrun", help="name of parkrun to process (defaults to 'Hartlepool'")
    ap.add_argument("-ev", "--event", help="event number to process (defaults to '1'")
    ap.add_argument("-th", "--thresh", help="threshold number of runs to include in statistics - runners with less than this number of runs are excluded (defaults to '1')")
    ap.add_argument("-lim", "--limit", help="Number of rows of statistics returned (defaults to '10')")
    ap.add_argument("-ob", "--orderBy", help="Order By (number: 1=total activities, 2=number of runs, 3=number of volunteerings, 4=time on feet)")
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
    db = parkrunDbLib(dbFname,Debug=(verbose>2))

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

    if (args.orderBy!=None):
        orderBy = int(args.orderBy)
    else:
        orderBy = 1

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
        getVolStats(db,parkrunStr,startTs,endTs,thresh,limit,orderBy)
    elif (cmdStr=="runstats"):
        getRunnerStats(db,parkrunStr,startTs,endTs,thresh,limit)
    else:
        print "ERROR: Command %s not recognised" % cmdStr


