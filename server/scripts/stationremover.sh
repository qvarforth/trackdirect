#!/bin/sh

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "$0 [config file path] [station id]"
    exit
fi

CONFIGFILE=$1
STATIONID=$2

if ps -ef | grep -v grep | grep "bin/stationremover.py $CONFIGFILE $STATIONID" ; then
    exit 0
else
    CURRENTDIR=$(dirname $0)

    export PYTHONPATH=$PYTHONPATH:$CURRENTDIR/../trackdirect
    cd $CURRENTDIR/..
    python $CURRENTDIR/../bin/stationremover.py $CONFIGFILE $STATIONID
    exit 0
fi
