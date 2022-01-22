create table station_telemetry_param (
    "id" bigserial not null,
    "station_id" bigint null,
    "created_ts" bigint default extract(epoch from now()),
    "latest_ts" bigint default extract(epoch from now()),
    "valid_to_ts" bigint null,
    "p1" text null,
    "p2" text null,
    "p3" text null,
    "p4" text null,
    "p5" text null,
    "b1" text null,
    "b2" text null,
    "b3" text null,
    "b4" text null,
    "b5" text null,
    "b6" text null,
    "b7" text null,
    "b8" text null,
    primary key (id),
    foreign key(station_id) references station(id)
);

create index station_telemetry_param_station_id_idx on station_telemetry_param(station_id, valid_to_ts, latest_ts);
