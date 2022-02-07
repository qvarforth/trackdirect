create table station_telemetry_eqns (
    "id" bigserial not null,
    "station_id" bigint null,
    "created_ts" bigint default extract(epoch from now()),
    "latest_ts" bigint default extract(epoch from now()),
    "valid_to_ts" bigint null,

    "a1" real null,
    "b1" real null,
    "c1" real null,

    "a2" real null,
    "b2" real null,
    "c2" real null,

    "a3" real null,
    "b3" real null,
    "c3" real null,

    "a4" real null,
    "b4" real null,
    "c4" real null,

    "a5" real null,
    "b5" real null,
    "c5" real null,

    primary key (id),
    foreign key(station_id) references station(id)
);

create index station_telemetry_eqns_station_id_idx on station_telemetry_eqns(station_id, valid_to_ts, latest_ts);
