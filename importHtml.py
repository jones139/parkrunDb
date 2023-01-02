#!/usr/bin/env python
""" Imports a folder of html files into the database.
It is assumed that each html file is a parkrun results page saved from the
web site.
"""
#import urllib
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
        print("Parkrun %s not in database - adding it" % prName)
        print(db.addParkrun(prName))
        prId = db.getParkrunId(prName)
    print("prId= %d " % prId)
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
    #print soup.find("h1").contents[0]
    prName  = soup.find("h1").contents[0].split('-')[0].split()[0]
    #print prName
    #print soup.find("h3").contents
    #dateStr = soup.find("h3").contents[0].split('-')[1].split()[0]
    dateStr = soup.find("h3").find("span").contents[0]
    eventNoStr = soup.find("h3").contents[2].contents[0]
    eventNo = int(eventNoStr.strip('#'))
    print(prName, eventNo, dateStr)

    dateTs = db.dateStr2ts(dateStr)

    prId = getParkrunId(db,prName)
    print("prId = %d" % prId)
    eventId = db.getEventId(prId,dateTs)
    if (eventId!=-1):
        print("Event already exists for  %s parkrun on %s - skipping file" \
            % (prName,dateStr))
        return None
    print("No event found in database for %s parkrun on %s - adding it" \
              % (prName,dateStr))
    eventId = db.addEvent(eventNo, prId, dateTs)

    print("eventId=%d" % eventId)
    resultsTable = soup.find( "table", {"class":"Results-table"})

    for row in resultsTable.findAll("tr", {"class":"Results-table-row"}):
        #print(row['data-name'])
        runnerName = row['data-name']
        finishPos = int(row['data-position'])
        if (runnerName != "Unknown"):
            runnerAgeCat = row['data-agegroup']
            runnerAgeGrade = row['data-agegrade']
            if (runnerAgeGrade == ""):
                runnerAgeGrade = "0"
            gender = row['data-gender']
            note = row['data-achievement']
            nRuns = row['data-runs']   
            club = row['data-club']


            # extract the barcode no (runnerNo) from the link in the table.
            href = row.find("td",{"class":"Results-table-td--name"}).find("a", href=True)
            print(href['href'])
            runnerNo = int(href['href'].split('/')[-1])
            timeParts = row.find("td",{"class":"Results-table-td--time"}).contents[0].contents[0].split(":")
            if (len(timeParts)==2):
                runnerTime = 60*int(timeParts[0])+int(timeParts[1])
            else:
                runnerTime = 3600*int(timeParts[0])+60*int(timeParts[1])+int(timeParts[2])
            try: 
                genderPos = row.find("td",{"class":"Results-table-td--gender"}).find("div",{"class":"detailed"}).contents[0].strip()
            except:
                genderPos = -1
            

            clubRowStr = row \
                         .find("td",{"class":"Results-table-td--club"})
            #print(clubRowStr)
            clubDiv = clubRowStr.find("div",{"class":"compact"})
            if (clubDiv is not None):
                clubStr = clubDiv.find("a",href=True)
                clubNo = clubStr['href'].split('=')[1]
            else:
                clubNo = -1

        else:
            print("Handling unknown runner")
            # Handle unknown runners
            runnerNo = 0
            runnerName = "Unknown"
            nRuns = 0
            club=""
            clubNo=9999
            gender=""
            genderPos= 9999
            timeParts="--:--"
            runnerTime= 9999
            runnerAgeCat=""
            runnerAgeGrade = 0.0
            note=""
            
        # print(runnerName, finishPos,runnerNo, timeParts, runnerTime, runnerAgeCat, runnerAgeGrade, gender, genderPos, club, clubNo, note, nRuns)
        
        roleId = 0  # 0 = run, 1 = volunteer
        runnerId = db.getRunnerId(runnerNo)
        if (runnerId==-1):
            print("No Runner found in database with Barcode ID %d - adding %s." \
                % (runnerNo, runnerName))
            runnerId = db.addRunner(runnerNo, runnerName, club,gender)
        else:
            # Check if we have complete runner data (check gender set)
            # (we won't if it was created as a volunteer)
            runnerData = db.getRunner(runnerId)
            if (runnerData[3]==""):
                #print "Updating Data for Runner %s." % runnerName
                db.updateRunner(runnerId,runnerNo,runnerName, club, gender)

        db.addRun(eventId, runnerId, roleId, runnerTime,
                  str(runnerAgeCat), float(runnerAgeGrade),
                  finishPos,genderPos,note)
    ###########################################
    # Now extract the names of the volunteers
    volTitleText = re.compile('Thanks to the volunteers')
    volPar = soup.find("h3",text=volTitleText).nextSibling
    volLinks = volPar.findAll("a")
    #print(volLinks)
    for volLink in volLinks:
        volName = volLink.contents[0]
        print(volLink)
        runnerNo = int(volLink['href'].split('=')[1].split('\\')[0])
        #print(volName,runnerNo)
        runnerId = db.getRunnerId(runnerNo)
        if (runnerId==-1):
            print("No Runner found in database with Barcode No %d - adding him/her." \
                % (runnerNo))
            runnerId = db.addRunner(runnerNo, volName, "","")

        roleId = 1  # 0 = run, 1 = volunteer
        db.addRun(eventId, runnerId, roleId, 9999,
                  "", 0.0,
                  0,0,"Volunteer")

        
    return partList



ap = argparse.ArgumentParser()
ap.add_argument("inDir", help="Directory containing the files to import (defaults to ./html_files")
ap.add_argument("-db", "--database", help="Filename of Database to use (Defaults to ./parkrun.db")

ap.add_argument("-v", "--verbose",
                help="produce verbose output for debugging",
                action="count")
args = ap.parse_args()

verbose = args.verbose
if (verbose): print(args)


inDir = args.inDir

if (args.database!=None):
    dbFname = args.database
else:
    dbFname = "./parkrun.db"


if (os.path.exists(inDir)):
    if (os.path.isdir(inDir)):
        if (verbose):
            print("Input Directory %s exists - OK" % inDir)
        if (os.path.exists(dbFname)):
            db = parkrunDbLib(dbFname, Debug=False)
            print("Opened Database")
            for root, dirs, files in os.walk(inDir):
                for file in files:
                    if (file.endswith(".html") | file.endswith(".htm") |
                    file.endswith(".HTML") | file.endswith(".HTM")):
                        print(os.path.join(root, file))
                        importHtmlFile(db,os.path.join(root,file))
        else:
            print("ERROR - Database file %s does not exist" % dbFname)
            exit(-1)
    else:
        print("ERROR:  %s exists, but is not a Directory" % inDir)
        exit(-1)
else:
    print("ERROR - %s does not exist" % inDir)
    exit(-1)



