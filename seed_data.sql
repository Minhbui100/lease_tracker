INSERT INTO property (address, city, state, zip, county, property_type, year_built, current_value, bedrooms, bathrooms, area, is_occupied)
VALUES
('123 Highway 6', 'Houston', 'TX', '77082', 'Harris', 'single-family', 1998, 285000.00, 3, 2.0, 1650, true),
('456 Bellaire Blvd', 'Houston', 'TX', '77036', 'Harris', 'single-family', 2005, 310000.00, 4, 2.5, 2100, false),
('789 Westheimer Rd', 'Houston', 'TX', '77042', 'Harris', 'multi-family', 2012, 450000.00, 2, 1.5, 950, true);

INSERT INTO tenant (first_name, last_name, dob, driver_license, phone, email)
VALUES
('Jane', 'Doe', '1990-04-12', 'TX12345678', '713-555-0101', 'jane.doe@email.com'),
('John', 'Smith', '1985-11-03', 'TX87654321', '713-555-0102', 'john.smith@email.com'),
('Maria', 'Garcia', '1992-07-22', 'TX55566677', '713-555-0103', NULL);

INSERT INTO lease (property_id, start_date, end_date, monthly_rent, rent_due_date, refundable_deposit, nonrefundable_deposit, cars, pets, status)
VALUES
(1, '2026-01-01', '2026-12-31', 1800.00, 1, 1800.00, 200.00, 1, 1, 'active'),
(3, '2026-03-15', '2027-03-14', 1200.00, 15, 1200.00, 150.00, 0, 0, 'active');

INSERT INTO lease_tenant (tenant_id, lease_id)
VALUES
(1, 1),  
(2, 1),  
(3, 2); 

INSERT INTO payment (lease_id, rent_due_date, amount, status)
VALUES
(1, '2026-08-01', 1800.00, 'paid'),
(1, '2026-09-01', 1800.00, 'pending'),
(2, '2026-08-15', 1200.00, 'late');

INSERT INTO maintenance_request (tenant_id, property_id, description, status, submission_time, material_cost, labor_cost, paid_by)
VALUES
(1, 1, 'Leaking kitchen faucet', 'open', NOW(), NULL, NULL, 'owner'),
(3, 3, 'AC unit not cooling properly', 'in_progress', NOW(), 85.00, 120.00, 'owner');

INSERT INTO emergency_contact (first_name, last_name, tenant_id, address, phone, email)
VALUES
('Robert', 'Doe', 1, '100 Main St, Houston, TX 77002', '713-555-0201', 'robert.doe@email.com'),
('Linda', 'Smith', 2, '200 Oak St, Houston, TX 77003', '713-555-0202', NULL);

INSERT INTO dependence (first_name, last_name, dob, relationship, lease_id)
VALUES
('Emily', 'Doe', '2015-06-01', 'daughter', 1),
('Lucas', 'Garcia', '2018-09-14', 'son', 2);

INSERT INTO image (link, property_id)
VALUES
('https://example.com/images/property1-front.jpg', 1),
('https://example.com/images/property1-kitchen.jpg', 1),
('https://example.com/images/property3-exterior.jpg', 3);
