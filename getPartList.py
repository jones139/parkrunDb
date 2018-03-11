#!/usr/bin/python

import urllib2
from bs4 import BeautifulSoup
import re
import json

baseUrl = "http://www.parkrun.org.uk/%s/results/eventhistory/"

def getEventsList(eventName):
    eventsList = []
    url = baseUrl % (eventName)
    print url
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    req = urllib2.Request(url,None,headers)
    response = urllib2.urlopen(req)
    print response.info()
    html = response.read()
    response.close()

    soup = BeautifulSoup(html, 'html.parser')

    resultsTable = soup.find( "table", {"id":"results"})
    for row in resultsTable.findAll("tr"):
        cells = row.findAll("td")
        if len(cells)>0:
            #print cells[1]
            href = cells[1].find("a", href=True)
            #print href['href']
            eventsList.append(href['href'])
    return eventsList


def getParticipants(eventName,resultUrl):
    partList = []
    eventUrl = baseUrl % (eventName)
    url = "%s%s" % (eventUrl,resultUrl)
    print url
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    req = urllib2.Request(url,None,headers)
    response = urllib2.urlopen(req)
    print response.info()
    html = response.read()
    response.close()

    soup = BeautifulSoup(html, 'html.parser')

    dateStr = soup.find("h2").contents[0].split('-')[1].split()[0]
    print dateStr
    
    resultsTable = soup.find( "table", {"id":"results"})
    for row in resultsTable.findAll("tr"):
        cells = row.findAll("td")
        if len(cells)>0:
            href = cells[1].find("a", href=True)
            if href!=None:
                runnerId = href['href'].split('=')[1]
                runnerName = href.contents[0]
                timeParts = cells[2].contents[0].split(':')
                if (len(timeParts)==2):
                    runnerTime = 60*int(timeParts[0])+int(timeParts[1])
                else:
                    runnerTime = 3600*int(timeParts[0])+60*int(timeParts[1])+int(timeParts[2])
                #print runnerName,timeParts,runnerTime
                pos = int(cells[0].contents[0])
                runnerAgeCat = cells[3].find("a").contents[0]
                gender = cells[5].contents[0]
                genderPos = int(cells[6].contents[0])
                #print(cells[7])
                if (len(cells[7].find("a").contents)>0):
                    club = cells[7].find("a").contents[0]
                else:
                    club=''
                note = cells[8].contents[0]
                nRuns = int(cells[9].contents[0])
                partList.append({
                    'pos':pos,
                    'id':runnerId,
                    'name':runnerName,
                    'activity':'run',
                    'runTime': runnerTime,
                    'ageCat': str(runnerAgeCat),
                    'gender': str(gender),
                    'genderPos': genderPos,
                    'club': str(club),
                    'note': str(note),
                    'nRuns': nRuns,
                    'date':dateStr
                })
    # Now extract the names of the volunteers
    volTitleText = re.compile('Thanks to the volunteers')
    volTitle = soup.find("h3",text=volTitleText)
    volParText = volTitle.next_sibling.contents[0].split(':')[1]
    #print volParText
    #volparText = volParText.split(':')[1]
    volList = volParText.split(', ')
    for volName in volList:
        partList.append({'id':'unknown','name':volName,'activity':'vol','date':dateStr})
    return partList



partList = []
el = getEventsList("hartlepool")
#print el

for n in range(0,55):
    pl = getParticipants("hartlepool",el[n])
    partList.extend(pl)

print partList
f = open('partlist.json','w')
json.dump(partList,f)
f.close()
