create table ogn_hidden_station (
    "id" bigserial not null,
    "hashed_name" text not null,
    primary key (id)
);

create index ogn_hidden_station_hashed_name_idx on ogn_hidden_station(hashed_name);
