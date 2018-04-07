#!/usr/bin/python
""" Calculates various statistics and produces output from parkrun database.
"""
from parkrunDbLib import parkrunDbLib
import argparse
import os

def getEventHistory(db,parkrunStr):
    """ Produce an event history summary """
    rows = db.getEventHistory(parkrunStr)

    for row in rows:
        print row


def getEventResults(db,parkrunStr,eventNo):
    """ Produce an event results summary """
    rows = db.getEventResults(parkrunStr,eventNo)
    for row in rows:
        print row
        
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("command", help="command to execute")
    ap.add_argument("-db", "--database", help="Filename of Database to use (Defaults to ./parkrun.db")
    ap.add_argument("-pr", "--parkrun", help="name of parkrun to process (defaults to 'Hartlepool'")
    ap.add_argument("-ev", "--event", help="event number to process (defaults to '1'")

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

    if (args.parkrun!=None):
        parkrunStr = args.parkrun
    else:
        parkrunStr = "Hartlepool"

    if (args.event!=None):
        eventNo = int(args.event)
    else:
        eventNo = 1
        
    db = parkrunDbLib(dbFname)

    if (cmdStr=="history"):
        getEventHistory(db,parkrunStr)
    elif (cmdStr=="results"):
        getEventResults(db,parkrunStr,eventNo)
    else:
        print "ERROR: Command %s not recognised" % cmdStr


