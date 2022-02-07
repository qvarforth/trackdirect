create table station_telemetry_bits (
    "id" bigserial not null,
    "station_id" bigint null,
    "created_ts" bigint default extract(epoch from now()),
    "latest_ts" bigint default extract(epoch from now()),
    "valid_to_ts" bigint null,
    "bits" text null,
    "title" text null,
    primary key (id),
    foreign key(station_id) references station(id)
);

create index station_telemetry_bits_station_id_idx on station_telemetry_bits(station_id, valid_to_ts, latest_ts);
