create table packet_path (
     "id" bigserial not null,
     "packet_id" bigint not null,
     "sending_station_id" bigint not null,
     "station_id" bigint not null,
     "latitude" double precision null,
     "longitude" double precision null,
     "timestamp" bigint null,
     "distance" int null,
     "number" smallint,
     primary key (id),
     foreign key(station_id) references station(id),
     foreign key(sending_station_id) references station(id)
);
