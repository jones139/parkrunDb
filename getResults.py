#!/usr/bin/env python

# Download parkrun results from web site, and save to a folder.
# ***WE ARE NOT ALLOWED OT USE THIS - Instead use a web browser to select the
#                                     event history, and open each results page
#                                     in turn and save it to the required folder.
#
# run ./getResults.py -h to see arguments.
#
# 06apr2018  GJ  ORIGINAL VERSION

import argparse
import os
import time
import urllib.request
from bs4 import BeautifulSoup
import re
import json
import random

def getEventsList(eventName):
    baseUrl = "http://www.parkrun.org.uk/%s/results/eventhistory/"
    eventsList = []
    url = baseUrl % (eventName)
    print(url)
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    req = urllib.request.Request(url,None,headers)
    response = urllib.request.urlopen(req)
    print(response.info())
    html = response.read()
    #print(html)
    response.close()

    soup = BeautifulSoup(html, 'html.parser')

    resultsTable = soup.find( "table", {"class":"Results-table"})
    #print(resultsTable)
    for row in resultsTable.findAll("tr"):
        #print(row)
        cells = row.findAll("td")
        #print(cells)
        if len(cells)>0:
            href = cells[1].find("a", href=True)
            hrefParts = href['href'].split("=")
            #print(href['href'],hrefParts,len(hrefParts))
            if (len(hrefParts)>1):
                eventsList.append(int(hrefParts[1]))
            else:
                eventsList.append(hrefParts[0])
    return eventsList




def getResultsHtml(eventName,eventNo):
    #baseUrl = "http://www.parkrun.org.uk/%s/results/weeklyresults/?runSeqNumber=%d"
    baseUrl = "http://www.parkrun.org.uk/%s/results/results/%d/"
    url = baseUrl % (eventName,eventNo)
    print(url)
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    req = urllib.request.Request(url,None,headers)
    response = urllib.request.urlopen(req)
    print(response.info())
    html = response.read()
    response.close()

    return html



ap = argparse.ArgumentParser()
ap.add_argument("eventMax", help="Highest Event Number to Retrieve")
ap.add_argument("-m", "--eventMin", help="Lowest Event Number to Retrieve (defaults to maximum")
ap.add_argument("-d", "--delay", help="Delay (in seconds) between downloading web pages (defaults to 5 seconds)")
ap.add_argument("-v", "--verbose",
                help="produce verbose output for debugging",
                action="count")
ap.add_argument("-p", "--parkrun",
                help="parkrun name - defaults to 'hartlepool'")
ap.add_argument("-o", "--outDir",
                help="Output Directory (defaults to ./output)")
args = ap.parse_args()

verbose = args.verbose
if (verbose): print(args)


if (args.parkrun!=None):
    parkrun = args.parkrun
else:
    parkrun = "hartlepool"

eventMax = int(args.eventMax)
if (args.eventMin!=None):
    eventMin = int(args.eventMin)
else:
    eventMin = eventMax

if (args.delay!=None):
    delay = int(args.delay)
else:
    delay = 5

if (args.outDir!=None):
    outDir = args.outDir
else:
    outDir = "./html_files"


eventList =  getEventsList(parkrun)
print("eventList=",eventList)

if (os.path.exists(outDir)):
    if (os.path.isdir(outDir)):
        if (verbose):
            print("Output Directory already exists - OK")
    else:
        print("ERROR:  %s exists, but is not a Directory" % outDir)
        exit(-1)
else:
    print("Creating output directory %s" % outDir)
    os.makedirs(outDir)


print(eventMin, eventMax)
for eventNo in range(eventMin,eventMax+1):
    if (True):
    #if (eventNo in eventList):
        print("Downloading Event No %d" % eventNo)
        h = getResultsHtml(parkrun,eventNo)
        fname = os.path.join(outDir,"%s_%d.html" % (parkrun,eventNo))
        if (verbose):  print ("fname=%s." % fname)
        f = open(fname,'w')
        f.write(str(h))
        f.close
        delayTime = delay * random.uniform(0.2, 2.0)
        print("Sleeping for %f seconds" % delayTime)
        time.sleep(delayTime)
    else:
        print("Event No %d not found" % eventNo)


