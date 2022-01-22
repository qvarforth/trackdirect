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

\i $SQLPATH/map.sql
\i $SQLPATH/marker.sql
\i $SQLPATH/ogn_address_type.sql
\i $SQLPATH/ogn_aircraft_type.sql
\i $SQLPATH/ogn_device.sql
\i $SQLPATH/ogn_hidden_station.sql
\i $SQLPATH/packet_type.sql
\i $SQLPATH/sender.sql
\i $SQLPATH/source.sql
\i $SQLPATH/station_type.sql
\i $SQLPATH/station.sql
\i $SQLPATH/station_telemetry_bits.sql
\i $SQLPATH/station_telemetry_eqns.sql
\i $SQLPATH/station_telemetry_param.sql
\i $SQLPATH/station_telemetry_unit.sql
\i $SQLPATH/packet.sql
\i $SQLPATH/packet_weather.sql
\i $SQLPATH/packet_telemetry.sql
\i $SQLPATH/packet_path.sql
\i $SQLPATH/packet_ogn.sql

commit;

EOF


exit 0
