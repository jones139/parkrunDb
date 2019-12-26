#!/bin/sh

python parkrunStats.py -sd 01/01/2019 -ed 31/12/2019 annual
python parkrunStats.py -sd 01/01/2014 -ed 31/12/2019 annual
rm -rf Hartlepool_All
mv Hartlepool_2014 Hartlepool_All

ncftpput -f ~/Dropbox/openseizuredetector.ftp -R /public_html/static  Hartlepool_2019\
ncftpput -f ~/Dropbox/openseizuredetector.ftp -R /public_html/static  Hartlepool_All\


#hartlepool_2018.html \
#	 styles.css \
#	 annual_attendance.png \
#	 weekly_attendance.png \
#	 weekly_First_Timers.png \
#	 weekly_PBs.png
