create table packet_ogn (
     "id" bigserial not null,
     "packet_id" bigint not null,
     "station_id" bigint not null,
     "timestamp" bigint not null,
     "ogn_sender_address" text null,
     "ogn_address_type_id" smallint null,
     "ogn_aircraft_type_id" smallint null,
     "ogn_climb_rate" int null,
     "ogn_turn_rate" float null,
     "ogn_signal_to_noise_ratio" float null,
     "ogn_bit_errors_corrected" int null,
     "ogn_frequency_offset" float null,
     primary key (id),
     foreign key(station_id) references station(id)
);
