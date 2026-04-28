-- USERS (Auth layer)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) CHECK (role IN ('user', 'admin')) NOT NULL
);

-- CUSTOMER
CREATE TABLE customers (
    customer_ssn VARCHAR(20) PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE customer_addresses (
    id SERIAL PRIMARY KEY,
    customer_ssn VARCHAR(20) REFERENCES customers(customer_ssn),
    street TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    apartment_no TEXT
);

-- BRANCH
CREATE TABLE branches (
    branch_id SERIAL PRIMARY KEY,
    name TEXT,
    city TEXT,
    address TEXT,
    assets NUMERIC
);

-- EMPLOYEE
CREATE TABLE employees (
    emp_ssn VARCHAR(20) PRIMARY KEY,
    name TEXT,
    branch_id INT REFERENCES branches(branch_id),
    manager_ssn VARCHAR(20) REFERENCES employees(emp_ssn),
    start_date DATE
);

CREATE TABLE employee_phones (
    id SERIAL PRIMARY KEY,
    emp_ssn VARCHAR(20) REFERENCES employees(emp_ssn),
    phone_number TEXT
);

CREATE TABLE employee_dependents (
    id SERIAL PRIMARY KEY,
    emp_ssn VARCHAR(20) REFERENCES employees(emp_ssn),
    dependent_name TEXT
);

-- ACCOUNT (SUPERCLASS)
CREATE TABLE accounts (
    account_number SERIAL PRIMARY KEY,
    balance NUMERIC DEFAULT 0
);

-- CUSTOMER ↔ ACCOUNT (M:N)
CREATE TABLE account_holders (
    customer_ssn VARCHAR(20),
    account_number INT,
    last_accessed TIMESTAMP,
    PRIMARY KEY (customer_ssn, account_number),
    FOREIGN KEY (customer_ssn) REFERENCES customers(customer_ssn),
    FOREIGN KEY (account_number) REFERENCES accounts(account_number)
);

-- ACCOUNT TYPES (ISA)
CREATE TABLE savings_accounts (
    account_number INT PRIMARY KEY REFERENCES accounts(account_number),
    fixed_interest_rate NUMERIC
);

CREATE TABLE checking_accounts (
    account_number INT PRIMARY KEY REFERENCES accounts(account_number),
    overdraft_limit NUMERIC
);

CREATE TABLE money_market_accounts (
    account_number INT PRIMARY KEY REFERENCES accounts(account_number),
    variable_interest_rate NUMERIC
);

-- LOAN
CREATE TABLE loan_accounts (
    account_number INT PRIMARY KEY REFERENCES accounts(account_number),
    fixed_interest_rate NUMERIC,
    monthly_payment NUMERIC
);

-- TRANSACTIONS
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    account_number INT REFERENCES accounts(account_number),
    amount NUMERIC NOT NULL,
    transaction_type VARCHAR(20),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_chargeable BOOLEAN
);

-- BRANCH RELATIONSHIPS
CREATE TABLE account_branches (
    account_number INT REFERENCES accounts(account_number),
    branch_id INT REFERENCES branches(branch_id),
    PRIMARY KEY (account_number, branch_id)
);

CREATE TABLE customer_banks_at (
    customer_ssn VARCHAR(20),
    branch_id INT,
    PRIMARY KEY (customer_ssn, branch_id),
    FOREIGN KEY (customer_ssn) REFERENCES customers(customer_ssn),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);