#!/bin/sh
if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "$0 [dbname] [dbport] [sqlpath]"
    exit
fi

DATABASE=$1
PORT=$2
SQLPATH=$3

# Assumes .pgpass is correctly set
psql -p $PORT $DATABASE << EOF

begin transaction;

\i $SQLPATH/01_map.sql
\i $SQLPATH/02_marker.sql
\i $SQLPATH/03_ogn_address_type.sql
\i $SQLPATH/04_ogn_aircraft_type.sql
\i $SQLPATH/05_ogn_device.sql
\i $SQLPATH/06_ogn_hidden_station.sql
\i $SQLPATH/07_packet_type.sql
\i $SQLPATH/08_sender.sql
\i $SQLPATH/09_source.sql
\i $SQLPATH/10_station_type.sql
\i $SQLPATH/11_station.sql
\i $SQLPATH/12_station_telemetry_bits.sql
\i $SQLPATH/13_station_telemetry_eqns.sql
\i $SQLPATH/14_station_telemetry_param.sql
\i $SQLPATH/15_station_telemetry_unit.sql
\i $SQLPATH/16_packet.sql
\i $SQLPATH/17_packet_weather.sql
\i $SQLPATH/18_packet_telemetry.sql
\i $SQLPATH/19_packet_path.sql
\i $SQLPATH/20_packet_ogn.sql

commit;

EOF


exit 0
