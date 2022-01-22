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
