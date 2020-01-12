README: parkrun_db
==================

This is a set of scripts that I use to maintain a database of results
for my local parkrun and produce annual statistics.

To use it you need to collect the html files of parkrun results and put them into a folder (e.g. ./html_files) - you can just save using the 'html only' option in the browser as we don't kneed all the images etc, just the text of the web page.

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
      'annual' - produce a folder with html file and images for an annual summary.

The output is not pretty for many of the options - just lists of numbers which you have to turn into something presentable, sorry!   This is what the 'annual' option attempts to do.

for 'volstats' the output is:
    Name,
    Barcode No,
    Number of Runs,
    Number of Volunteers,
    Total (runs+volunteers)
    Time Running (sec)
    Time Volunteering (sec) (Set to zero)
    Time on Feet (Sec)
