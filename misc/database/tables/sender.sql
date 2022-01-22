create table sender (
    "id" bigserial not null,
    "name" text not null,
    primary key (id)
);

create index sender_name_idx on sender(name);
