#!/usr/bin/python

from parkrunDbLib import parkrunDbLib

DEBUG = True
dbFname = "parkrun.db"

db = parkrunDbLib("parkrun.db")

print "PARKRUNS"
print db.getParkruns()
print
print "EVENTS"
print db.getEvents(0)
print
print "EVENTS - 2018"
print db.getEvents(0,"2018-01-01")

