drop table if exists users;
create table users (
  username string primary key,
  password string not null,
  usertype string not null
);