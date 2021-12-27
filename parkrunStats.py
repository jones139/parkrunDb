#!/usr/bin/python
""" Calculates various statistics and produces output from parkrun database.
"""
from parkrunDbLib import parkrunDbLib
import argparse
import os
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
#  import time
import errno
import shutil
import numpy as np

# To get rid of a matplotlib warning!
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

def getAnnualSummary(db,parkrunStrArr,startTs,endTs, tableLen=10):
    """ Produce an HTML summary of the given period.
    """
    print("getAnnualSummary - startTs=%s, endTs=%s" % (startTs, endTs))
    parkrunStr = ""
    first = True
    for prStr in parkrunStrArr:
        if (first):
            parkrunStr = "%s" % prStr
            first = False
        else:
            parkrunStr = "%s-%s" % (parkrunStr, prStr)

    print("parkrunStr = %s" % parkrunStr)
        
    dirName = "%s_%s" % (parkrunStr,
                         dt.datetime.fromtimestamp(startTs).strftime('%Y'))
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
    of.write("<title>%s Parkrun</title>\n" % parkrunStr)
    of.write("<link rel='stylesheet' href='styles.css'>")
    of.write("</head>\n")
    of.write("<body>\n")
    of.write("<h1 id='top'>Summary for %s Parkrun %s to %s</h1>\n" %\
             (parkrunStr,db.ts2dateStr(startTs), db.ts2dateStr(endTs)))
    of.write("<a href='../All/index.html'>All Years</a> | ")
    of.write("<a href='../2014/index.html'>2014</a> | ")
    of.write("<a href='../2015/index.html'>2015</a> | ")
    of.write("<a href='../2016/index.html'>2016</a> | ")
    of.write("<a href='../2017/index.html'>2017</a> | ")
    of.write("<a href='../2018/index.html'>2018</a> | ")
    of.write("<a href='../2019/index.html'>2019</a> | ")
    of.write("<a href='../2020/index.html'>2020</a> | ")
    of.write("<a href='../2021/index.html'>2021</a>  \n")
    of.write("<hr>\n")
    of.write("<a href='#annual_attendance'>Annual Attendance</a> | ")
    of.write("<a href='#graphs'>Graphs</a> | ")
    of.write("<a href='#runs'>Most Runs</a> | ")
    of.write("<a href='#timeonfeet'>Time on Feet</a> | ")
    of.write("<a href='#volunteers'>Volunteers</a> | ")
    of.write("<a href='#keenest'>Keenest</a> | ")
    of.write("<a href='#consistency'>Consistency</a> | ")
    of.write("<hr>\n")
    
    of.write("<h2 id='annual_attendance'>Annual Attendance</h2>\n")
    of.write("<a href='#top'>Top of Page</a><br/>")
    of.write("<table>\n")
    of.write("<tr>")
    of.write("<th>Year</th>")
    of.write("<th>Number of Events</th>")
    of.write("<th>Average Attendance</th>")
    of.write("<th>Number of Runs</th>")
    of.write("<th>Number of Volunteers</th>")
    of.write("<th>Number of PBs</th>")
    of.write("<th>Number of First Timers</th>")
    of.write("<th>Mean Run Time (min)</th>")
    of.write("</tr>\n")

    rows = db.getEventAttendanceSummary(parkrunStrArr[0],
                                        db.dateStr2ts("01/01/2000"),
                                        endTs)
    graphX = []
    graphAnnualAtt = []
    graphAverageAtt = []
    for row in rows:
        of.write("<tr>")
        of.write("<td>%s</td>" % row[0])
        of.write("<td>%s</td>" % row[1])
        of.write("<td>%d</td>" % int(row[2]/row[1]))
        of.write("<td>%s</td>" % row[2])
        of.write("<td>%s</td>" % row[3])
        of.write("<td>%s</td>" % row[4])
        of.write("<td>%s</td>" % row[5])
        of.write("<td>%3.1f</td>" % (
            float(row[6]/row[7]/60.)
        ) )
        of.write("</tr>\n")
        graphX.append(row[0])
        graphAnnualAtt.append(row[2])
        graphAverageAtt.append(row[2]/row[1])
    of.write("</table>")

    # Make annual attendance graph
    fig, ax = plt.subplots()
    bar1 = ax.bar(graphX,graphAnnualAtt)
    ax.set_xlabel('Year')
    ax.set_ylabel('Total Runs')
    plt.title('%s Parkrun Annual Attendance' % parkrunStrArr[0])
    plt.savefig(os.path.join(dirName,'annual_attendance.png'))

    # Make average attendance graph
    fig, ax = plt.subplots()
    bar1 = ax.bar(graphX,graphAverageAtt)
    ax.set_xlabel('Year')
    ax.set_ylabel('%s Parkrun Average Attendance' % parkrunStrArr[0])
    plt.title('%s Parkrun Average Attendance' % parkrunStrArr[0])
    plt.savefig(os.path.join(dirName,'average_annual_attendance.png'))

    
    of.write('<img src="annual_attendance.png" '\
             'alt="Annual Attendance Graph" '\
             'style="width:500px;height:300px;">\n')
    of.write('<img src="average_annual_attendance.png" '\
             'alt="Average Annual Attendance Graph" '\
             'style="width:500px;height:300px;">\n')
    
    
    of.write("<h2 id='graphs'>Statistics for Events between %s and %s</h2>\n" \
             % (db.ts2dateStr(startTs), db.ts2dateStr(endTs)))
    of.write("<a href='#top'>Top of Page</a><br/>")
    rows = db.getEventHistory(parkrunStrArr[0],startTs,endTs)
    graphX = []
    graphY = []
    for row in rows:
        # Convert unix timestamp to python datetime objects
        graphX.append(dt.datetime.fromtimestamp(row[2]))
        graphY.append(row[4])
    # Make graph
    fig, ax = plt.subplots()
    bar1 = ax.plot(graphX,graphY)
    ax.grid()
    ax.set_xlabel('Date')
    ax.set_ylabel('Attendance')
    if (endTs-startTs) > (400*24*3600):  # 400 days
        print("Long time range - using YearLocator....tsDiff=%d" % (endTs-startTs))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    else:
        print("Short time range - using MonthLocator....tsDiff=%d" % (endTs-startTs))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
    plt.title('%s Parkrun Attendance' % parkrunStrArr[0])
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(dirName,'weekly_attendance.png'))

    maxAttendance = max(graphY)
    minAttendance = min(graphY)
    of.write("Max Attendance = %d, Min Attendance = %d <br>"
             % (maxAttendance,
                minAttendance))
    of.write('<img src="weekly_attendance.png" '\
             'alt="Weekly Attendance Graph" '\
             'style="width:500px;height:300px;">\n')

    #Run Time Histogram
    getTimeHistogram(db, parkrunStrArr[0], startTs, endTs, dirName)
    of.write('<img src="finish_time_hist.png" '\
             'alt="Finish Time Histogram" '\
             'style="width:500px;height:300px;">\n')

    of.write("<br/>\n");

    # Weekly PBs Graph
    #of.write("<h2>Weekly PBs</h2>\n")
    of.write('<img src="weekly_PBs.png" '\
             'alt="Weekly PBs Graph" '\
             'style="width:500px;height:300px;">\n')
    rows = db.getEventHistory(parkrunStrArr[0],startTs,endTs)
    graphX = []
    graphY = []
    for row in rows:
        # Drop the first event, because everyone was a first timer!
        if(row[0]>1):
            #graphX.append(row[0])
            # Convert unix timestamp to python datetime objects
            graphX.append(dt.datetime.fromtimestamp(row[2]))
            graphY.append(row[6])
        else:
            print("Ignoring Event %d for first timer's graph" % row[0])
            print(row)
    # Make graph
    fig, ax = plt.subplots()
    if (endTs-startTs) > (400*24*3600):  # 400 days
        print("Long time range - using YearLocator....tsDiff=%d" % (endTs-startTs))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    else:
        print("Short time range - using MonthLocator....tsDiff=%d" % (endTs-startTs))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
    bar1 = ax.plot(graphX,graphY)
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of PBs')
    ax.grid()

    plt.title('Number of PBs at Each Parkrun')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(dirName,'weekly_PBs.png'))

    # Weekly First Timers Graph
    #of.write("<h2>Weekly First Timers</h2>\n")
    of.write('<img src="weekly_First_Timers.png" '\
             'alt="Weekly First Timers Graph" '\
             'style="width:500px;height:300px;">\n')
    rows = db.getEventHistory(parkrunStrArr[0],startTs,endTs)
    graphX = []
    graphY = []
    for row in rows:
        # Skip first event where everyone was a first timer
        if (row[0]>1):
            #graphX.append(row[0])
            # Convert unix timestamp to python datetime objects
            graphX.append(dt.datetime.fromtimestamp(row[2]))
            graphY.append(row[7])
            #print(row)
    # Make graph
    fig, ax = plt.subplots()
    if (endTs-startTs) > (400*24*3600):  # 400 days
        print("Long time range - using YearLocator....tsDiff=%d" % (endTs-startTs))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    else:
        print("Short time range - using MonthLocator....tsDiff=%d" % (endTs-startTs))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
    bar1 = ax.plot(graphX,graphY)
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of First Timers')
    ax.grid()
    plt.title('Number of First Timers at Each Parkrun')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(dirName,'weekly_First_Timers.png'))


    ###############################################
    of.write("<h2 id='top_participants'>Top Participants</h2>\n")

    of.write("<h3 id='runs'>Most Runs</h3>\n")
    of.write("<a href='#top'>Top of Page</a><br/>")
    of.write("<p>Total Number of Runs in the period</p>\n")
    of.write("<table>\n")
    of.write("<tr>")
    of.write("<th></th>")
    of.write("<th>Name</th>")
    of.write("<th>Number of Runs</th>")
    of.write("<th>Number of Volunteers</th>")
    of.write("</tr>\n")

    # Sort by number of runs (orderBy=2)
    rows = db.getVolStats(parkrunStrArr,startTs,endTs,1,tableLen+1,2)

    n = 0
    for row in rows:
        if (row[1]!=0):   # Ignore 'Unknown'
            #print row
            n += 1
            of.write("<tr>")
            of.write("<td>%d</td>" % n)
            of.write("<td>%s</td>" % row[0])
            of.write("<td>%s</td>" % row[2])
            of.write("<td>%s</td>" % row[3])
            of.write("</tr>\n")
    of.write("</table>")

    of.write("<h3 id='timeonfeet'>Time on Feet</h3>\n")
    of.write("<a href='#top'>Top of Page</a><br/>")
    of.write("<p>Total time spent running in the period.</p>\n")
    of.write("<table>\n")
    of.write("<tr>")
    of.write("<th></th>")
    of.write("<th>Name</th>")
    of.write("<th>Time on Feet (hours)</th>")
    of.write("</tr>\n")

    # Sort by time on feet (orderBy=4)
    rows = db.getVolStats(parkrunStrArr,startTs,endTs,1,tableLen+1,4)

    n = 0
    for row in rows:
        if (row[1]!=0):   # Ignore 'Unknown'
            #print row
            n += 1
            of.write("<tr>")
            of.write("<td>%d</td>" % n)
            of.write("<td>%s</td>" % row[0])
            timeonfeetSec = float(row[7])
            timeonfeetHour = timeonfeetSec / 3600.
            of.write("<td>%2.1f</td>" % timeonfeetHour)
            of.write("</tr>\n")
    of.write("</table>")

    of.write("<h3 id='volunteers'>Top Volunteers</h3>\n")
    of.write("<a href='#top'>Top of Page</a><br/>")
    of.write("<p>Total number of volunteering events</p>\n")
    of.write("<table>\n")
    of.write("<tr>")
    of.write("<th></th>")
    of.write("<th>Name</th>")
    of.write("<th>Number of Volunteers</th>")
    of.write("<th>Number of Runs</th>")
    of.write("</tr>\n")

    # Sort by number of volunteers (orderBy=3)
    rows = db.getVolStats(parkrunStrArr,startTs,endTs,1,tableLen+1,3)

    n = 0
    for row in rows:
        if (row[1]!=0):   # Ignore 'Unknown'
            #print row
            n += 1
            of.write("<tr>")
            of.write("<td>%d</td>" % n)
            of.write("<td>%s</td>" % row[0])
            of.write("<td>%s</td>" % row[3])
            of.write("<td>%s</td>" % row[2])
            of.write("</tr>\n")
    of.write("</table>")
    
    of.write("<h3 id='keenest'>Keenest</h3>\n")
    of.write("<a href='#top'>Top of Page</a><br/>")
    of.write("<p>Total Participation (run + volunteer). Note: Running and volunteering on the same day counts.</p>\n")
    of.write("<table>\n")
    of.write("<tr>")
    of.write("<th></th>")
    of.write("<th>Name</th>")
    of.write("<th>Number of Runs</th>")
    of.write("<th>Number of Volunteers</th>")
    of.write("<th>Total</th>")
    of.write("</tr>\n")

    # Sort by total number of activities (orderBy=1)
    rows = db.getVolStats(parkrunStrArr,startTs,endTs,1,tableLen+1,1)

    print("Processing Keenest....")
    n = 0
    for row in rows:
        if (row[1]!=0):   # Ignore 'Unknown'
            #print row
            n += 1
            of.write("<tr>")
            of.write("<td>%d</td>" % n)
            of.write("<td>%s</td>" % row[0])
            of.write("<td>%s</td>" % row[2])
            of.write("<td>%s</td>" % row[3])
            of.write("<td>%s</td>" % row[4])
            of.write("</tr>\n")
    of.write("</table>")




    of.write("<h3 id='consistency'>Consistency</h3>\n")
    of.write("<a href='#top'>Top of Page</a><br/>")
    of.write("<p>Smallest variation (standard deviation) in run times.</p>\n")
    of.write("<table>\n")
    of.write("<tr>")
    of.write("<th></th>")
    of.write("<th>Name</th>")
    of.write("<th>Run Time SD (sec)</th>")
    of.write("<th>Number of Runs</th>")
    of.write("</tr>\n")

    rows = getRunnerStats(db,parkrunStrArr[0],startTs,endTs,10,tableLen)
    
    n = 0
    for row in rows:
        if (row[1]!=0):   # Ignore 'Unknown'
            n += 1
            #print row
            of.write("<tr>")
            of.write("<td>%d</td>" % n)
            of.write("<td>%s</td>" % row[0])
            of.write("<td>%4.1f</td>" % row[3])
            of.write("<td>%d</td>" % row[1])
            of.write("</tr>\n")
    of.write("</table>\n")


    of.write("<h1 id='about'>About</h1>\n")
    of.write("<p>Summary Produced by <a href='https://github.com/jones139/parkrunDb'>parkrunStats.py<a> by Graham Jones, using data from published parkrun results.  Please email graham@openseizuredetector.org.uk with any issues or suggestions.   <a href='http://openseizuredetector.org.uk'>OpenSeizureDetector</a></p>\n")

    of.write("</body>\n")
    of.write("</html>\n")
    
    of.close()
    print()
    print("Output File %s is stored in directory %s" % \
          (outFname, dirName))
    print("*****************")
    print("*     DONE!     *")
    print("*****************")

def getTimeHistogram(db,parkrunStr,startTs,endTs, outDir="."):
    eventRows = db.getEventHistory(parkrunStr,startTs,endTs)

    runTimes = []
    for eventRow in eventRows:
        eventNo = eventRow[0]
        runRows = db.getEventResults(parkrunStr,eventNo)
        for runRow in runRows:
            # print(runRow)
            # the 9000 check is because the unknown runner gets
            # a time of 9999 seconds, which messes up the numbers!
            if (runRow[0]>0 and (runRow[2]<9000)):
                runTimes.append(runRow[2]/60.)
    #print(runTimes)
    runTimesArr = np.array(runTimes)
    print("Min Time  is %8.0f min" % np.min(runTimesArr))
    print("Mean Time  is %8.0f min" % np.mean(runTimesArr))
    print("Median Time  is %8.0f min" % np.median(runTimesArr))
    print("Max Time  is %8.0f min" % np.max(runTimesArr))
    print("StDev Time is %8.0f min" % np.std(runTimesArr))
    hist = np.histogram(runTimesArr,90,(1,90))
    graphX = range(1,91)
    print(len(hist[0]),len(graphX))
    print(graphX)
    print(hist[0])
    fig, ax = plt.subplots()
    bar1 = ax.plot(graphX,hist[0])
    ax.set_xlabel('Time(min)')
    ax.set_xticks(range(0,95,5))
    ax.set_ylabel('Runs')
    ax.grid()
    plt.title('%s Parkrun Finish Time Distribution\n%s to %s (Median=%2.0f min)' %
              (parkrunStr,
               db.ts2dateStr(startTs),
               db.ts2dateStr(endTs),
               np.median(runTimesArr)
              ))
    plt.savefig(os.path.join(outDir,'finish_time_hist.png'))
    print("Histogram stored as finish_time_hist.png")

    
def getEventHistory(db,parkrunStr,startTs,endTs):
    """ Produce an event history summary """
    rows = db.getEventAttendanceSummary(parkrunStr,startTs,endTs)
    print("Annual Summary")
    for row in rows:
        print(row)
    rows = db.getEventHistory(parkrunStr,startTs,endTs)
    print("All Events")
    for row in rows:
        print(row)


def getEventResults(db,parkrunStr,eventNo):
    """ Produce an event results summary """
    rows = db.getEventResults(parkrunStr,eventNo)
    for row in rows:
        print(row)

def getVolStats(db,parkrunStr,startTs,endTs,thresh,limit,orderBy):
    """ produce volunteer statistics for each participant
    """
    rows = db.getVolStats(parkrunStr,startTs,endTs,thresh,limit,orderBy)
    for row in rows:
        print(row)

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
    print("getRunnerStats()")
    rows = db.getRunnerList(parkrunStr,startTs,endTs,thresh,10000)
    resultsArr = []
    for row in rows:
        #print row
        if (row[1]=="Unknown"):
            print("Ignoring the Unknown Runner....")
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

    ap.add_argument("-v", "--verbose", default=0,
                    help="produce verbose output for debugging",
                    action="count")
    args = ap.parse_args()

    verbose = args.verbose
    if (verbose): print(args)


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

    if (verbose): print("startTs = %d (%s)" % (startTs,db.ts2dateStr(startTs)))
    if (verbose): print("endTs = %d (%s)" % (endTs,db.ts2dateStr(endTs)))
        

    
    parkrunStrParts = parkrunStr.split(",")
    if (',' in parkrunStr):
        print("contains comma!!!")
    parkrunStrArr = []
    for prStr in parkrunStrParts:
        parkrunStrArr.append(prStr)
    print(parkrunStrArr)
        
    
    if (cmdStr=="history"):
        getEventHistory(db,parkrunStr,startTs,endTs)
    elif (cmdStr=="results"):
        getEventResults(db,parkrunStr,eventNo)
    elif (cmdStr=="timeHistogram"):
        getTimeHistogram(db,parkrunStr,startTs,endTs)
    elif (cmdStr=="volstats"):
        getVolStats(db,parkrunStr,startTs,endTs,thresh,limit,orderBy)
    elif (cmdStr=="runstats"):
        resultsArr = getRunnerStats(db,parkrunStr,startTs,endTs,thresh,limit)
        for r in resultsArr:
            print(r)
    elif (cmdStr=="annual"):
        getAnnualSummary(db,parkrunStrArr,startTs,endTs,limit)
    else:
        print("ERROR: Command %s not recognised" % cmdStr)


