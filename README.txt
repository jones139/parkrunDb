README: parkrun_db
==================

Collect the html files of parkrun results and put them into a folder ./html_files

Add any new volunteers that have not run before into iddb.json to assign them a barcode number.

*** NOTE - this will erase the entire database!!!! ****
Initialise the database with:
        sqlite3 parkrun.db <createdb.sqlite

Import the data files into the database with:
	time ./importHtml.py  ./html_files/ >import.txt

It should complete without errors.

Produce some statistics with:
	./parkrunStats.py -h
shows the command line parameters.  Valid commands are:
      'history' - produce a version of the parkrun event history from the database,
      'results' - produce a version of the parkrun results table from the database,
      'volstats' - calculate statistics related to volunteering (it also does time on feet).
      'runstats' - calculate statistics on runs - in particular the standard deviation of run time (with outliers removed) used for the 'consistency' award.

The output is not pretty - just lists of numbers which you have to turn into something presentable, sorry!

for 'volstats' the output is:
    Name,
    Barcode No,
    Number of Runs,
    Number of Volunteers,
    Total (runs+volunteers)
    Time Running (sec)
    Time Volunteering (sec) (Set to zero)
    Time on Feet (Sec)
