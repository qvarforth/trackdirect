create table map (
    "id" smallint not null,
    "name" text not null,
    primary key (id)
);

insert into map(id, name) values(1, 'Show on map');
insert into map(id, name) values(2, 'Hide, same position as newer packet');
insert into map(id, name) values(3, 'Hide, duplicate packet');
insert into map(id, name) values(4, 'Hide, failed to find marker id');
insert into map(id, name) values(5, 'Hide, faulty gps position');
insert into map(id, name) values(6, 'Hide, packet received to late');
insert into map(id, name) values(7, 'Hide, moves to fast');
insert into map(id, name) values(8, 'Hide, packet is less than 5 seconds after previous');
insert into map(id, name) values(9, 'Hide, abnormal position');
insert into map(id, name) values(10, 'Hide, has no position');
insert into map(id, name) values(11, 'Hide, unsupported format');
insert into map(id, name) values (12, 'Hide, same position as newer packet (but later date)');
insert into map(id, name) values (13, 'Hide, same position as newer packet (and faulty gps position)');
insert into map(id, name) values (14, 'Hide, killed object/item');
insert into map(id, name) values (15, 'Stealth/No tracking');
insert into map(id, name) values (16, 'Faulty network, APRS packet digipeated by a CWOP-station');
