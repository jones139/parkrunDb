#!/bin/sh

python parkrunStats.py -sd 01/01/2019 -ed 31/12/2019 annual


ncftpput -f ~/Dropbox/openseizuredetector.ftp -R /public_html/static  Hartlepool_2019\


#hartlepool_2018.html \
#	 styles.css \
#	 annual_attendance.png \
#	 weekly_attendance.png \
#	 weekly_First_Timers.png \
#	 weekly_PBs.png
