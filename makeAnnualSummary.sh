#!/bin/bash

YEARS=(2014 2015 2016 2017 2018 2019 )
PARKRUNS=( "Hartlepool,Rossmere" "Hartlepool" "Rossmere" )

# DO Annual stats
for PARKRUN in ${PARKRUNS[@]}; do
    echo $PARKRUN
    OUTDIR=${PARKRUN//[,]/-}
    echo $OUTDIR
    for YEAR in ${YEARS[@]}; do
	echo $YEAR
	python parkrunStats.py -pr $PARKRUN -sd 01/01/$YEAR -ed 31/12/$YEAR annual
	ncftpput -f ~/Dropbox/openseizuredetector.ftp -R /public_html/static  ${OUTDIR}_${YEAR}
    done
    # Do All Time Stats
    python parkrunStats.py -pr $PARKRUN -sd 01/01/1970 -ed 31/12/2100 annual
    rm -rf ${OUTDIR}_All
    mv ${OUTDIR}_1970 ${OUTDIR}_All
    ncftpput -f ~/Dropbox/openseizuredetector.ftp -R /public_html/static  ${OUTDIR}_All
done






#hartlepool_2018.html \
#	 styles.css \
#	 annual_attendance.png \
#	 weekly_attendance.png \
#	 weekly_First_Timers.png \
#	 weekly_PBs.png
