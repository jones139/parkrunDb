#!/bin/bash

YEARS=(2019 2018)
PARKRUNS=( "Hartlepool" "Rossmere" )

# DO Annual stats
for PARKRUN in ${PARKRUNS[@]}; do
    echo $PARKRUN
    for YEAR in ${YEARS[@]}; do
	echo $YEAR
	python parkrunStats.py -pr $PARKRUN -sd 01/01/$YEAR -ed 31/12/$YEAR annual
	ncftpput -f ~/Dropbox/openseizuredetector.ftp -R /public_html/static  ${PARKRUN}_${YEAR}
    done
    # Do All Time Stats
    python parkrunStats.py -pr $PARKRUN -sd 01/01/1970 -ed 31/12/2100 annual
    rm -rf ${PARKRUN}_All
    mv ${PARKRUN}_1970 ${PARKRUN}_All
    ncftpput -f ~/Dropbox/openseizuredetector.ftp -R /public_html/static  ${PARKRUN}_All
done






#hartlepool_2018.html \
#	 styles.css \
#	 annual_attendance.png \
#	 weekly_attendance.png \
#	 weekly_First_Timers.png \
#	 weekly_PBs.png
