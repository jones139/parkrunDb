#!/usr/bin/python
""" Imports a folder of html files into the database.
It is assumed that each html file is a parkrun results page saved from the
web site.
"""
import urllib2
from bs4 import BeautifulSoup
import re
from parkrunDbLib import parkrunDbLib
import json
import argparse
import os

def getParkrunId(db,prName):
    """ 
    find the Id of parkrun named prName in sqlite parkrunLib database db.
    if prName is not in the database, it is added and the new ID returned.
    """
    prId = db.getParkrunId(prName)
    if (prId==-1):
        print "Parkrun %s not in database - adding it" % prName
        print db.addParkrun(prName)
        prId = db.getParkrunId(prName)
    print "prId= %d " % prId
    return prId

def importHtmlFile(db,fname):
    partList = []

    # read all the text of the file into htmlStr
    f = open(fname,"r")
    htmlStr = f.read()
    #print html
    f.close()

    soup = BeautifulSoup(htmlStr, 'html.parser')

    # Get event details
    print soup.find("h2").contents[0]
    prName  = soup.find("h2").contents[0].split('-')[0].split()[0]
    eventNo = soup.find("h2").contents[0].split('-')[0].split()[3]
    dateStr = soup.find("h2").contents[0].split('-')[1].split()[0]
    print prName, eventNo, dateStr

    dateTs = db.dateStr2ts(dateStr)

    prId = getParkrunId(db,prName)
    print "prId = %d" % prId
    eventId = db.getEventId(prId,dateTs)
    if (eventId==-1):
        print "No event found in database for %s parkrun on %s - adding it" \
            % (prName,dateStr)
        eventId = db.addEvent(eventNo, prId, dateTs)

    print "eventId=%d" % eventId
    resultsTable = soup.find( "table", {"id":"results"})
    for row in resultsTable.findAll("tr"):
        cells = row.findAll("td")
        if len(cells)>0:
            finishPos = int(cells[0].contents[0])
            href = cells[1].find("a", href=True)
            if href!=None:
                print "Prcessing Runner ",href
                runnerNo = int(href['href'].split('=')[1])
                runnerName = href.contents[0]
                timeParts = cells[2].contents[0].split(':')
                if (len(timeParts)==2):
                    runnerTime = 60*int(timeParts[0])+int(timeParts[1])
                else:
                    runnerTime = 3600*int(timeParts[0])+60*int(timeParts[1])+int(timeParts[2])
                #print runnerName,timeParts,runnerTime
                runnerAgeCat = cells[3].find("a").contents[0]
                #print cells[3],runnerAgeCat
                runnerAgeGrade = cells[4].contents[0].split('%')[0]
                #print cells[4],runnerAgeGrade
                gender = cells[5].contents[0]
                genderPos = int(cells[6].contents[0])
                #print(cells[7])
                if (len(cells[7].find("a").contents)>0):
                    club = cells[7].find("a").contents[0]
                else:
                    club=''
                note = cells[8].contents[0]
                nRuns = int(cells[9].contents[0])
            else:
                print "Handling unknown runner"
                # Handle unknown runners
                runnerNo = 0
                runnerName = "Unknown"
                club=""
                gender=""
                genderPos= 9999
                runnerTime= 9999
                runnerAgeCat=""
                runnerAgeGrade = 0.0
                note=""
            roleId = 0  # 0 = run, 1 = volunteer
            runnerId = db.getRunnerId(runnerNo)
            if (runnerId==-1):
                print "No Runner found in database with Barcode ID %d - adding him/her." \
                    % (runnerNo)
                runnerId = db.addRunner(runnerNo, runnerName, club,gender)
            else:
                # Check if we have complete runner data (check gender set)
                # (we won't if it was created as a volunteer)
                runnerData = db.getRunner(runnerId)
                if (runnerData[3]==""):
                    db.updateRunner(runnerId,runnerNo,runnerName, club, gender)

            db.addRun(eventId, runnerId, roleId, runnerTime,
                      str(runnerAgeCat), float(runnerAgeGrade),
                      finishPos,genderPos,note)
    # Now extract the names of the volunteers
    volTitleText = re.compile('Thanks to the volunteers')
    volTitle = soup.find("h3",text=volTitleText)
    volParText = volTitle.next_sibling.contents[0].split(':')[1]
    #print volParText
    #volparText = volParText.split(':')[1]
    volList = volParText.split(', ')
    for volName in volList:
        runnerNo = db.getRunnerNoFromName(volName)
        if (runnerNo==-1):
            print ("**** ERROR:  Failed to Find Volunteer %s in Database ****" % volName)
            print ("    Please add entry to external id database and re-import")
        else:
            print ("Found Runner %s - barcode = A%s." % (volName,runnerNo))
        # this runnerNo might have come from the external database, so check the
        # main DB, and add the volunteer if necessary.
        runnerId = db.getRunnerId(runnerNo)
        if (runnerId==-1):
            print "No Runner found in database with Barcode No %d - adding him/her." \
                % (runnerNo)
            runnerId = db.addRunner(runnerNo, volName, "","")

        roleId = 1  # 0 = run, 1 = volunteer
        db.addRun(eventId, runnerId, roleId, 9999,
                  "", 0.0,
                  0,0,"Volunteer")

        
    return partList



ap = argparse.ArgumentParser()
ap.add_argument("inDir", help="Directory containing the files to import (defaults to ./html_files")
ap.add_argument("-db", "--database", help="Filename of Database to use (Defaults to ./parkrun.db")
ap.add_argument("-id", "--iddb", help="Filename of external id lookup database (Defaults to None")

ap.add_argument("-v", "--verbose",
                help="produce verbose output for debugging",
                action="count")
args = ap.parse_args()

verbose = args.verbose
if (verbose): print args


inDir = args.inDir

if (args.database!=None):
    dbFname = args.database
else:
    dbFname = "./parkrun.db"

if (args.iddb!=None):
    iddb = args.iddb
else:
    iddb = None


if (os.path.exists(inDir)):
    if (os.path.isdir(inDir)):
        if (verbose):
            print "Input Directory %s exists - OK" % inDir
        if (os.path.exists(dbFname)):
            db = parkrunDbLib(dbFname,iddb)
            print "Opened Database"
            for root, dirs, files in os.walk(inDir):
                for file in files:
                    if (file.endswith(".html") | file.endswith(".htm") |
                    file.endswith(".HTML") | file.endswith(".HTM")):
                        print(os.path.join(root, file))
                        importHtmlFile(db,os.path.join(root,file))
        else:
            print "ERROR - Database file %s does not exist" % dbFname
            exit(-1)
    else:
        print "ERROR:  %s exists, but is not a Directory" % inDir
        exit(-1)
else:
    print "ERROR - %s does not exist" % inDir
    exit(-1)



