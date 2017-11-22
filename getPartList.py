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
                partList.append({'id':runnerId,'name':runnerName,'activity':'run','date':dateStr})
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

for n in range(0,27):
    pl = getParticipants("hartlepool",el[n])
    partList.extend(pl)

print partList
f = open('partlist.json','w')
json.dump(partList,f)
f.close()
