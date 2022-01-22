#!/bin/sh
if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "$0 [config file] [destination directory]"
    exit
fi

CONFIGFILE=$1

if ps -ef | grep -v grep | grep "bin/heatmapcreator.py $CONFIGFILE"; then
    exit 0
else
    cd ..
    CURRENTDIR=$(dirname $0)
    DESTDIR=$2

    export PYTHONPATH=$PYTHONPATH:$CURRENTDIR/../trackdirect:$CURRENTDIR/../../heatmap-2.2.1/
    cd $CURRENTDIR/..
    python2 $CURRENTDIR/../bin/heatmapcreator.py $CONFIGFILE $DESTDIR 2>&1 &
    exit 0
fi
