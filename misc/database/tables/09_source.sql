create table source (
    "id" smallint not null,
    "name" text not null,
    primary key (id)
);


insert into source(id, name) values(1, 'APRS');
insert into source(id, name) values(2, 'CWOP');
insert into source(id, name) values(3, 'CBAPRS');
insert into source(id, name) values(4, 'HUBHAB');
insert into source(id, name) values(5, 'OGN');
