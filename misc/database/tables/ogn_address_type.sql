create table ogn_address_type (
    "id" smallint not null,
    "name" text not null,
    primary key (id)
);

insert into ogn_address_type(id, name) values(1, 'ICAO');
insert into ogn_address_type(id, name) values(2, 'FLARM');
insert into ogn_address_type(id, name) values(3, 'OGN');
