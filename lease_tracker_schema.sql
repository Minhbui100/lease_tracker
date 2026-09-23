--create database lease_tracker;
--\c lease_tracker;

create table property(
    id              serial          primary key,
    address         varchar(250)    not null,
    city            varchar(100)    not null,
    state           varchar(100)    not null,
    zip             varchar(100)    not null,
    county          varchar(100)    not null,
    property_type   varchar(100)    not null check (property_type in ('single-family', 'multi-family')),
    year_built      integer,
    current_value   numeric(12,2),
    bedrooms        integer,
    bathrooms       numeric (3,2), 
    area            numeric (12,2), --sqare footage
    is_occupied     boolean         default false,
    created_at      timestamp       default now()
);


create table tenant(
    id              serial          primary key,
    first_name      varchar (100)   not null,
    last_name       varchar (100)   not null,
    dob             date,
    driver_license  varchar (30),
    phone           varchar (20),
    email           varchar (200),
    created_at      timestamp       default now()
);


create table lease(
    id              serial          primary key,
    property_id     integer         not null        references property(id) on delete cascade,
    start_date      date            not null,
    end_date        date            not null,
    monthly_rent    numeric (10,2)  not null,
    rent_due_date   integer         not null check (rent_due_date between 1 and 28),
    refundable_deposit          numeric (10,2),
    nonrefundable_deposit       numeric (10,2),
    cars            integer,
    pets            integer,
    status          varchar(20)     default 'active' check(status in ('active', 'expired', 'terminated')),
    created_at      timestamp       default now(),
    check (end_date > start_date)
);


create table lease_tenant (
    tenant_id       integer         not null        references tenant(id) on delete cascade,
    lease_id        integer         not null        references lease(id) on delete cascade,
    primary key(tenant_id, lease_id)
);


--new pending payments are automatically created at the beginning of every month
create table payment (
    id              serial          primary key,
    lease_id        integer         not null        references lease(id) on delete cascade,
    due_date        date            not null,
    amount          numeric (10,2)  not null,
    memo            varchar(50),
    pay_style       varchar(20),
    status          varchar (20)    default 'pending' check(status in ('pending', 'paid', 'late')),
    created_at      timestamp       DEFAULT NOW()
);


create table payment (
    id              serial          primary key,
    lease_id        integer         not null        references lease(id) on delete cascade,
    due_date        date            not null,
    amount          numeric (10,2)  not null,
    memo            varchar (50),
    pay_type        varchar (20)    check(pay_type in ('check', 'cash', 'zelle', 'bank transfer')),
    status          varchar (20)    default 'pending' check(status in ('pending', 'paid', 'late')),
    created_at      timestamp       DEFAULT NOW()
);


create table maintenance_request(
    id              serial          primary key,
    tenant_id       integer         references tenant(id) on delete set null, 
    property_id     integer         not null        references property(id) on delete cascade,
    description     text            not null,
    status          varchar (20)    default 'open' check (status in ('open', 'in_progress', 'resolved')),
    submission_time timestamp,       
    resolution_time timestamp,
    material_cost   numeric (20,2),
    labor_cost      numeric (20,2),
    paid_by         varchar (20)    default 'owner' check (paid_by in ('owner', 'renter')),
    created_at      timestamp       DEFAULT NOW()
);


create table emergency_contact(
    id              serial          primary key,
    first_name      varchar (100)   not null,
    last_name       varchar (100)   not null,   
    tenant_id       integer         not null        references tenant(id) on delete cascade,
    address         varchar (500),
    phone           varchar (30)    not null,
    email           varchar (200)
);


create table dependence(
    id              serial          primary key,
    first_name      varchar (100)   not null,
    last_name       varchar (100)   not null,   
    dob             date,
    relationship    varchar (50)    not null,
    lease_id        integer         not null        references lease(id) on delete cascade
);


create table image(
    id              serial          primary key,
    link            text            not null,
    property_id     integer         not null        references property(id) on delete cascade
);