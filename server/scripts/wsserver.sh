#!/bin/sh
if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "$0 [config file]"
    exit
fi

CONFIGFILE=$1

if ps -eo pid,pgid,cmd | grep -v grep | grep "bin/wsserver.py --config $CONFIGFILE" ; then
    exit 0
else
    CURRENTDIR=$(dirname $0)

    export PYTHONPATH=$PYTHONPATH:$CURRENTDIR/../trackdirect
    cd $CURRENTDIR/..
    python $CURRENTDIR/../bin/wsserver.py --config $CONFIGFILE
    exit 0
fi
