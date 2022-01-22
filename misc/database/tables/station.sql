create table station (
    "id" bigserial not null,
    "name" text null,
    "latest_sender_id" bigint null,
    "station_type_id" smallint not null,
    "source_id" smallint not null,

    "latest_location_packet_id" bigint null,
    "latest_location_packet_timestamp" bigint null,
    "latest_location_marker_id" bigint null,
    "latest_location_symbol" text null,
    "latest_location_symbol_table" text null,
    "latest_location_latitude" double precision null,
    "latest_location_longitude" double precision null,

    "latest_confirmed_packet_id" bigint null,
    "latest_confirmed_packet_timestamp" bigint null,
    "latest_confirmed_marker_id" bigint null,
    "latest_confirmed_symbol" text null,
    "latest_confirmed_symbol_table" text null,
    "latest_confirmed_latitude" double precision null,
    "latest_confirmed_longitude" double precision null,

    "latest_packet_id" bigint null,
    "latest_packet_timestamp" bigint null,

    "latest_weather_packet_id" bigint null,
    "latest_weather_packet_timestamp" bigint null,
    "latest_weather_packet_comment" text null,

    "latest_telemetry_packet_id" bigint null,
    "latest_telemetry_packet_timestamp" bigint null,

    "latest_ogn_packet_id" bigint null,
    "latest_ogn_packet_timestamp" bigint null,
    "latest_ogn_sender_address" text null,
    "latest_ogn_aircraft_type_id" smallint null,
    "latest_ogn_address_type_id" smallint null,

    primary key (id),
    foreign key(latest_sender_id) references sender(id),
    foreign key(station_type_id) references station_type(id),
    foreign key(source_id) references source(id),
    foreign key(latest_ogn_aircraft_type_id) references ogn_aircraft_type(id),
    foreign key(latest_ogn_address_type_id) references ogn_address_type(id)
);

create index station_name_idx on station(name);
create index station_latest_sender_id_idx on station(latest_sender_id);
create index station_pos_timestamp_idx on station(latest_confirmed_latitude, latest_confirmed_longitude, latest_confirmed_packet_timestamp);
create index station_ogn_sender_address_idx on station(latest_ogn_sender_address);
