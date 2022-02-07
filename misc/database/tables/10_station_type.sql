create table station_type (
    "id" smallint not null,
    "name" text not null,
    primary key (id)
);


insert into station_type(id, name) values(1, 'Station');
insert into station_type(id, name) values(2, 'Object');
