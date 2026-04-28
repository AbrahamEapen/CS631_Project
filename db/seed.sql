--  CLEAN START (optional)
DROP TABLE IF EXISTS employee_phone CASCADE;
DROP TABLE IF EXISTS dependent CASCADE;
DROP TABLE IF EXISTS account_holder CASCADE;
DROP TABLE IF EXISTS transaction CASCADE;
DROP TABLE IF EXISTS account CASCADE;
DROP TABLE IF EXISTS employee CASCADE;
DROP TABLE IF EXISTS customer CASCADE;
DROP TABLE IF EXISTS branch CASCADE;
DROP TABLE IF EXISTS users CASCADE;

--  USERS
INSERT INTO users (id, username, password_hash, role)
VALUES
(1, 'admin', 'hashed_admin_password', 'admin'),
(2, 'john_doe', 'hashed_password1', 'user'),
(3, 'jane_smith', 'hashed_password2', 'user');

-- CUSTOMERS (mapped to users in your logic layer)
INSERT INTO customer (customer_ssn, name)
VALUES
('CUST001', 'John Doe'),
('CUST002', 'Jane Smith');

-- BRANCHES
INSERT INTO branch (branch_id, name, city, address, assets)
VALUES
(1, 'Main Branch', 'New York', '123 Wall Street', 5000000),
(2, 'West Branch', 'Los Angeles', '456 Sunset Blvd', 3000000);

-- ACCOUNTS
INSERT INTO account (account_number, balance)
VALUES
(1001, 1500.00),
(1002, 2500.00),
(1003, 500.00);

-- ACCOUNT HOLDERS (M:N)
INSERT INTO account_holder (customer_ssn, account_number)
VALUES
('CUST001', 1001),
('CUST001', 1002),
('CUST002', 1003);

-- TRANSACTIONS (TEST SCENARIOS)

-- John Doe account activity
INSERT INTO transaction (transaction_id, account_number, amount, transaction_type, transaction_date)
VALUES
(1, 1001, 500.00, 'deposit', NOW() - INTERVAL '5 days'),
(2, 1001, 200.00, 'withdraw', NOW() - INTERVAL '4 days'),
(3, 1001, 300.00, 'deposit', NOW() - INTERVAL '3 days');

-- Second account activity (John)
INSERT INTO transaction (transaction_id, account_number, amount, transaction_type, transaction_date)
VALUES
(4, 1002, 1000.00, 'deposit', NOW() - INTERVAL '2 days'),
(5, 1002, 150.00, 'withdraw', NOW() - INTERVAL '1 day');

-- Jane account activity
INSERT INTO transaction (transaction_id, account_number, amount, transaction_type, transaction_date)
VALUES
(6, 1003, 500.00, 'deposit', NOW() - INTERVAL '6 days');

-- EMPLOYEES
INSERT INTO employee (emp_ssn, name, branch_id, manager_ssn)
VALUES
('EMP001', 'Alice Manager', 1, NULL),
('EMP002', 'Bob Teller', 1, 'EMP001'),
('EMP003', 'Charlie Assistant', 2, 'EMP001');

-- EMPLOYEE PHONES
INSERT INTO employee_phone (emp_ssn, phone)
VALUES
('EMP001', '555-1000'),
('EMP002', '555-1001'),
('EMP003', '555-1002');

--  DEPENDENTS
INSERT INTO dependent (emp_ssn, dependent_name, relationship)
VALUES
('EMP002', 'Sarah Doe', 'Spouse'),
('EMP003', 'Tom Junior', 'Child');