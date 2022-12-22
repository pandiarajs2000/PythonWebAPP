show databases;
use InventoryDB;

-- create table for product

create table product
(
    product_id varchar(255) primary key,
    product_desc varchar(255)
);

-- insert values of product table
insert into product ('product_id','product_desc') values ('Bag','Lunch Bag');
insert into product ('product_id','product_desc') values ('Table','Study Table');

-- create tabel for location

create tabel location 
(
    location_id varchar(255) primary key,
    location_desc varchar(255)
);

-- insert values of location table
insert into product ('location_id','location_desc') values ('Madurai','Near Bus Stand');

-- create table for productmovement
create table productmovements
(
    movement_id int not null auto_increment primary key,
    product_id varchar(255),
	date_time timestamp,
	from_location varchar(255),
	to_location varchar(255),
    qty int,
	foreign key(product_id) references products(product_id)
);