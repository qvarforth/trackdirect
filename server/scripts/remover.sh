#!/bin/sh

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "$0 [config file path]"
    exit
fi

CONFIGFILE=$1

if ps -ef | grep -v grep | grep "bin/remover.py $CONFIGFILE" ; then
    exit 0
else
    CURRENTDIR=$(dirname $0)

    export PYTHONPATH=$PYTHONPATH:$CURRENTDIR/../trackdirect
    cd $CURRENTDIR/..
    python $CURRENTDIR/../bin/remover.py $CONFIGFILE
    exit 0
fi
