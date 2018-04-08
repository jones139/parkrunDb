#!/usr/bin/python
"""
Tests for parkrunDb
"""
import unittest
import json
from parkrunDbLib import parkrunDbLib

class dbTests(unittest.TestCase):
    def setUp(self):
        print "setup()"
        self.db = parkrunDbLib("test.db")
        self.db.initialiseDb("createdb.sqlite")
        

class TestDates(dbTests):
    def testDateConv(self):
        dateStr = "31/01/2018"
        ts = self.db.dateStr2ts(dateStr)
        dateStr2 = self.db.ts2dateStr(ts)
        print "DateStr=%s, ts=%d, DateStr2=%s" % (dateStr,ts,dateStr2)
        self.assertEqual(dateStr,dateStr2)

class TestEvents(dbTests):
    def testAddEvent(self):
        dateStr = "31/01/2018"
        eventNo = 999
        prId = 1
        evId = self.db.addEvent(eventNo,prId,self.db.dateStr2ts(dateStr))
        evId2 = self.db.getEventId(prId,self.db.dateStr2ts(dateStr))
        self.assertEqual(evId,evId2)

        evId3 = self.db.getEventIdFromEventNo(prId,eventNo)
        self.assertEqual(evId,evId3)
        
    def testAddRun(self):
        dateStr = "31/01/2018"
        eventNo = 999
        prId = 1
        evId = self.db.addEvent(eventNo,prId,self.db.dateStr2ts(dateStr))

        runnerId = 1
        roleId = 1

        self.assertEqual(self.db.getRunId(evId,runnerId,roleId),-1)
        runId = self.db.addRun(evId,runnerId,roleId,999,"V45",60.2,1,3,"Note")
        runId2 = self.db.getRunId(evId,runnerId,roleId)
        self.assertEqual(runId,runId2)
        
    def testAddRunner(self):
        self.assertEqual(self.db.getRunnerId(123456),-1)
        runnerId = self.db.addRunner(123456,"Blogs, Joe","HBRH","V45")
        runnerId2 = self.db.getRunnerId(123456)
        self.assertEqual(runnerId,runnerId2)

        runnerId = self.db.addRunner(1234567,"Blogs, Joe2","HBRH","F40")
        runnerId2 = self.db.getRunnerId(1234567)
        self.assertEqual(runnerId,runnerId2)

    def testFindRunner(self):
        self.db = parkrunDbLib("test.db","iddb.json")
        self.db.initialiseDb("createdb.sqlite")

        nameStr = "Roy WATKINS"
        runnerId = self.db.getRunnerIdFromName(nameStr)
        self.assertEqual(runnerId,1455360)

        nameStr = "NON EXISTANT RUNNER"
        runnerId = self.db.getRunnerIdFromName(nameStr)
        self.assertEqual(runnerId,-1)

        


if __name__ == '__main__':
    unittest.main()
