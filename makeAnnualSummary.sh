#!/bin/bash

#YEARS=(2014 2015 2016 2017 2018 2019 2020 2021 2022 2023)
YEARS=( 2023 )
#PARKRUNS=( "Hartlepool,Rossmere" "Hartlepool" "Rossmere" )
PARKRUNS=( "Hartlepool" )

# DO Annual stats
for PARKRUN in ${PARKRUNS[@]}; do
    echo $PARKRUN
    OUTDIR=${PARKRUN//[,]/-}
    echo $OUTDIR
    for YEAR in ${YEARS[@]}; do
	echo $YEAR
	python parkrunStats.py -pr $PARKRUN -sd 01/01/$YEAR -ed 31/12/$YEAR annual --limit=10
	ncftpput -m -f ~/Dropbox/openseizuredetector.ftp -R /public_html/static/Parkrun/${OUTDIR}/${YEAR} ${OUTDIR}_${YEAR}/*
    done
    # Do All Time Stats
    python parkrunStats.py -pr $PARKRUN -sd 01/01/2013 -ed 31/12/2100 annual --limit=10
    rm -rf ${OUTDIR}_All
    mv ${OUTDIR}_2013 ${OUTDIR}_All
    ncftpput -m -f ~/Dropbox/openseizuredetector.ftp -R /public_html/static/Parkrun/${OUTDIR}/All  ${OUTDIR}_All/*
done






#hartlepool_2018.html \
#	 styles.css \
#	 annual_attendance.png \
#	 weekly_attendance.png \
#	 weekly_First_Timers.png \
#	 weekly_PBs.png
