create table packet_type (
    "id" smallint not null,
    "name" text not null,
    primary key (id)
);


insert into packet_type(id, name) values(1, 'position');
insert into packet_type(id, name) values(2, 'direction');
insert into packet_type(id, name) values(3, 'weather');
insert into packet_type(id, name) values(4, 'object');
insert into packet_type(id, name) values(5, 'item');
insert into packet_type(id, name) values(6, 'telemetry');
insert into packet_type(id, name) values(7, 'message');
insert into packet_type(id, name) values(8, 'query');
insert into packet_type(id, name) values(9, 'response');
insert into packet_type(id, name) values(10, 'status');
insert into packet_type(id, name) values(11, 'other');
