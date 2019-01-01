#!/usr/bin/python
""" Calculates various statistics and produces output from parkrun database.
"""
from parkrunDbLib import parkrunDbLib
import argparse
import os
import math
import matplotlib.pyplot as plt
import datetime
import time
import errno
import shutil

def getAnnualSummary(db,parkrunStr,startTs,endTs):
    """ Produce an HTML summary of the given period.
    """
    print("getAnnualSummary - startTs=%s, endTs=%s" % (startTs, endTs))
    dirName = "%s_%s" % (parkrunStr,
                         datetime.datetime.fromtimestamp(startTs).strftime('%Y'))
    outFname = "index.html"
    try:
        os.makedirs(dirName)
    except OSError as exc:  
        if exc.errno == errno.EEXIST and os.path.isdir(dirName):
            pass
        else:
            raise
    # copy the CSS style file into the output directory.
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    shutil.copyfile(os.path.join(scriptDir,"styles.css"), \
                    os.path.join(dirName,"styles.css"))

    # Create the output html file.
    of = open(os.path.join(dirName,outFname),'w')
    if (of==None):
        print("ERROR OPENING output file")
        exit(-1)

    of.write("<html>\n")
    of.write("<head>\n")
    of.write("<title>Annual Summary for %s Parkrun</title>\n" % parkrunStr)
    of.write("<link rel='stylesheet' href='styles.css'>")
    of.write("</head>\n")
    of.write("<body>\n")
    of.write("<h1>Annual Summary for %s Parkrun</h1>\n" % parkrunStr)

    of.write("<h2>Annual Attendance</h2>\n")
    of.write("<table>\n")
    of.write("<tr>")
    of.write("<th>Year</th>")
    of.write("<th>Number of Events</th>")
    of.write("<th>Number of Runs</th>")
    of.write("<th>Number of Volunteers</th>")
    of.write("<th>Number of PBs</th>")
    of.write("<th>Number of First Timers</th>")
    of.write("</tr>\n")

    rows = db.getEventAttendanceSummary(parkrunStr,
                                        db.dateStr2ts("01/01/2000"),
                                        endTs)
    graphX = []
    graphY = []
    for row in rows:
        of.write("<tr>")
        of.write("<td>%s</td>" % row[0])
        of.write("<td>%s</td>" % row[1])
        of.write("<td>%s</td>" % row[2])
        of.write("<td>%s</td>" % row[3])
        of.write("<td>%s</td>" % row[4])
        of.write("<td>%s</td>" % row[5])
        of.write("</tr>\n")
        graphX.append(row[0])
        graphY.append(row[2])
    of.write("</table>")
    # Make annual attendance graph
    fig, ax = plt.subplots()
    bar1 = ax.bar(graphX,graphY)
    ax.set_xlabel('Year')
    ax.set_ylabel('Runs')
    plt.title('Annual Attendance')
    plt.savefig(os.path.join(dirName,'annual_attendance.png'))

    of.write('<img src="annual_attendance.png" '\
             'alt="Annual Attendance Graph" '\
             'style="width:500px;height:300px;">\n')
    
    
    of.write("<h2>Statistics for Events between %s and %s</h2>\n" \
             % (db.ts2dateStr(startTs), db.ts2dateStr(endTs)))
    of.write('<img src="weekly_attendance.png" '\
             'alt="Weekly Attendance Graph" '\
             'style="width:500px;height:300px;">\n')
    rows = db.getEventHistory(parkrunStr,startTs,endTs)
    graphX = []
    graphY = []
    for row in rows:
        graphX.append(row[0])
        graphY.append(row[4])
        #print(row)
    # Make graph
    fig, ax = plt.subplots()
    bar1 = ax.bar(graphX,graphY)
    ax.set_xlabel('Event Number')
    ax.set_ylabel('Runs')
    plt.title('Number of Participants at Each Parkrun')
    plt.savefig(os.path.join(dirName,'weekly_attendance.png'))

    # Weekly PBs Graph
    #of.write("<h2>Weekly PBs</h2>\n")
    of.write('<img src="weekly_PBs.png" '\
             'alt="Weekly PBs Graph" '\
             'style="width:500px;height:300px;">\n')
    rows = db.getEventHistory(parkrunStr,startTs,endTs)
    graphX = []
    graphY = []
    for row in rows:
        graphX.append(row[0])
        graphY.append(row[6])
        #print(row)
    # Make graph
    fig, ax = plt.subplots()
    bar1 = ax.bar(graphX,graphY)
    ax.set_xlabel('Event Number')
    ax.set_ylabel('PBs')
    plt.title('Number of PBs at Each Parkrun')
    plt.savefig(os.path.join(dirName,'weekly_PBs.png'))

    # Weekly Firs Timers Graph
    #of.write("<h2>Weekly First Timers</h2>\n")
    of.write('<img src="weekly_First_Timers.png" '\
             'alt="Weekly First Timers Graph" '\
             'style="width:500px;height:300px;">\n')
    rows = db.getEventHistory(parkrunStr,startTs,endTs)
    graphX = []
    graphY = []
    for row in rows:
        graphX.append(row[0])
        graphY.append(row[7])
        #print(row)
    # Make graph
    fig, ax = plt.subplots()
    bar1 = ax.bar(graphX,graphY)
    ax.set_xlabel('Event Number')
    ax.set_ylabel('First Timers')
    plt.title('Number of First Timers at Each Parkrun')
    plt.savefig(os.path.join(dirName,'weekly_First_Timers.png'))


    ###############################################
    of.write("<h2>Top Participants</h2>\n")

    of.write("<h3>Keenest</h3>\n")
    of.write("<table>\n")
    of.write("<tr>")
    of.write("<th>Name</th>")
    of.write("<th>Number of Runs</th>")
    of.write("<th>Number of Volunteers</th>")
    of.write("<th>Total</th>")
    of.write("</tr>\n")

    # Sort by total number of activities (orderBy=1)
    rows = db.getVolStats(parkrunStr,startTs,endTs,1,6,1)

    print("Processing Keenest....")
    for row in rows:
        if (row[1]!=0):   # Ignore 'Unknown'
            print row
            of.write("<tr>")
            of.write("<td>%s</td>" % row[0])
            of.write("<td>%s</td>" % row[2])
            of.write("<td>%s</td>" % row[3])
            of.write("<td>%s</td>" % row[4])
            of.write("</tr>\n")
    of.write("</table>")



    of.write("<h3>Most Runs</h3>\n")
    of.write("<table>\n")
    of.write("<tr>")
    of.write("<th>Name</th>")
    of.write("<th>Number of Runs</th>")
    of.write("<th>Number of Volunteers</th>")
    of.write("</tr>\n")

    # Sort by number of runs (orderBy=2)
    rows = db.getVolStats(parkrunStr,startTs,endTs,1,6,2)

    for row in rows:
        if (row[1]!=0):   # Ignore 'Unknown'
            #print row
            of.write("<tr>")
            of.write("<td>%s</td>" % row[0])
            of.write("<td>%s</td>" % row[2])
            of.write("<td>%s</td>" % row[3])
            of.write("</tr>\n")
    of.write("</table>")

    of.write("<h3>Time on Feet</h3>\n")
    of.write("<table>\n")
    of.write("<tr>")
    of.write("<th>Name</th>")
    of.write("<th>Time on Feet (hours)</th>")
    of.write("</tr>\n")

    # Sort by time on feet (orderBy=4)
    rows = db.getVolStats(parkrunStr,startTs,endTs,1,6,4)

    for row in rows:
        if (row[1]!=0):   # Ignore 'Unknown'
            #print row
            of.write("<tr>")
            of.write("<td>%s</td>" % row[0])
            timeonfeetSec = float(row[7])
            timeonfeetHour = timeonfeetSec / 3600.
            of.write("<td>%2.1f</td>" % timeonfeetHour)
            of.write("</tr>\n")
    of.write("</table>")

    of.write("<h3>Consistency</h3>\n")
    of.write("<table>\n")
    of.write("<tr>")
    of.write("<th>Name</th>")
    of.write("<th>Run Time SD (sec)</th>")
    of.write("</tr>\n")

    rows = getRunnerStats(db,parkrunStr,startTs,endTs,10,5)
    
    for row in rows:
        if (row[1]!=0):   # Ignore 'Unknown'
            print row
            of.write("<tr>")
            of.write("<td>%s</td>" % row[0])
            of.write("<td>%4.1f</td>" % row[3])
            of.write("</tr>\n")
    of.write("</table>")


    
    of.write("<h3>Top Volunteers</h3>\n")
    of.write("<table>\n")
    of.write("<tr>")
    of.write("<th>Name</th>")
    of.write("<th>Number of Runs</th>")
    of.write("<th>Number of Volunteers</th>")
    of.write("</tr>\n")

    # Sort by number of volunteers (orderBy=3)
    rows = db.getVolStats(parkrunStr,startTs,endTs,1,5,3)

    for row in rows:
        if (row[1]!=0):   # Ignore 'Unknown'
            #print row
            of.write("<tr>")
            of.write("<td>%s</td>" % row[0])
            of.write("<td>%s</td>" % row[2])
            of.write("<td>%s</td>" % row[3])
            of.write("</tr>\n")
    of.write("</table>")

    of.write("</body>\n")
    of.write("</html>\n")
    
    of.close()
    print()
    print("Output File %s is stored in directory %s" % \
          (outFname, dirName))
    print("*****************")
    print("*     DONE!     *")
    print("*****************")

    
def getEventHistory(db,parkrunStr,startTs,endTs):
    """ Produce an event history summary """
    rows = db.getEventAttendanceSummary(parkrunStr,startTs,endTs)
    print("Annual Summary")
    for row in rows:
        print row
    rows = db.getEventHistory(parkrunStr,startTs,endTs)
    print("All Events")
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
        if (nT>1):
            stDev = math.sqrt(stDev/(nT-1))
        else:
            stDev = 0

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
    #print "Sorted Results..."
    #for r in resultsArr[0:limit]:
    #    print r
    return resultsArr[0:limit]
            
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
        resultsArr = getRunnerStats(db,parkrunStr,startTs,endTs,thresh,limit)
        for r in resultsArr:
            print r
    elif (cmdStr=="annual"):
        getAnnualSummary(db,parkrunStr,startTs,endTs)
    else:
        print "ERROR: Command %s not recognised" % cmdStr


