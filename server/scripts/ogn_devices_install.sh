#!/bin/bash
if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "$0 [config file]"
    exit
fi

CONFIGFILE=$1
if [[ "$CONFIGFILE" != /* ]]; then
    CONFIGFILE="$HOME/trackdirect/config/$CONFIGFILE"
fi

if [ ! -f "$CONFIGFILE" ]; then
    echo "Config file $CONFIGFILE does not exist"
    exit
fi

# Parse database credentials from the .ini config file
DB_HOST=$(grep -oP '^host\s*=\s*\K.*' "$CONFIGFILE" | head -1)
DB_PORT=$(grep -oP '^port\s*=\s*\K.*' "$CONFIGFILE" | head -1)
DB_NAME=$(grep -oP '^database\s*=\s*\K.*' "$CONFIGFILE" | head -1)
DB_USER=$(grep -oP '^username\s*=\s*\K.*' "$CONFIGFILE" | head -1)
DB_PASS=$(grep -oP '^password\s*=\s*\K.*' "$CONFIGFILE" | head -1)

# Export password so psql doesn't need .pgpass
export PGPASSWORD="$DB_PASS"

pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd -P`
popd > /dev/null

# Create dir and remove old stuff (keep zip-file since it may be equal to latest)
mkdir -p $SCRIPTPATH/ogndevices
mkdir -p $SCRIPTPATH/ogndevices/${DB_NAME}
rm $SCRIPTPATH/ogndevices/${DB_NAME}/*.csv
rm $SCRIPTPATH/ogndevices/${DB_NAME}/*.txt
cd $SCRIPTPATH/ogndevices/${DB_NAME}

# Download latest csv file (but only if newer)
wget -N http://ddb.glidernet.org/download/?t=1 -O ogndevices.csv

if test `find "ogndevices.csv" -cmin +30`
then
    echo "File is not updated, skip reload of database."
else


# Remove comments in file
sed '/^#/ d' < ogndevices.csv > ogndevices2.csv

# Load file into database (password comes from PGPASSWORD env var)
psql -h $DB_HOST -p $DB_PORT $DB_NAME -U $DB_USER << EOF

create table if not exists ogn_device (
    "device_type" text not null,
    "device_id" text not null,
    "aircraft_model" text not null,
    "registration" text not null,
    "cn" text not null,
    "tracked" text not null,
    "identified" text not null,
    "ddb_aircraft_type" text not null
);

begin transaction;

drop index if exists ogn_device_device_id_idx;
truncate ogn_device;
\copy ogn_device from '$SCRIPTPATH/ogndevices/$DB_NAME/ogndevices2.csv' DELIMITERS ',' CSV QUOTE '''';
create index ogn_device_device_id_idx on ogn_device(device_id);

insert into ogn_device(device_type, device_id, aircraft_model, registration, cn, tracked, identified, ddb_aircraft_type) values ('F', '3FEF6F', '', '', '', 'N', 'N', 1);
commit;

EOF

fi

exit 0