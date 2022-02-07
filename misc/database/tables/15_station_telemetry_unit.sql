create table station_telemetry_unit (
    "id" bigserial not null,
    "station_id" bigint null,
    "created_ts" bigint default extract(epoch from now()),
    "latest_ts" bigint default extract(epoch from now()),
    "valid_to_ts" bigint null,
    "u1" text null,
    "u2" text null,
    "u3" text null,
    "u4" text null,
    "u5" text null,
    "l1" text null,
    "l2" text null,
    "l3" text null,
    "l4" text null,
    "l5" text null,
    "l6" text null,
    "l7" text null,
    "l8" text null,
    primary key (id),
    foreign key(station_id) references station(id)
);

create index station_telemetry_unit_station_id_idx on station_telemetry_unit(station_id, valid_to_ts, latest_ts);
