CREATE DATABASE myuser;

CREATE DATABASE airflow;
GRANT ALL PRIVILEGES ON DATABASE airflow TO myuser;

DROP TABLE IF EXISTS dev_customers, dev_roles, dev_tg_users, dev_employees CASCADE;

-- Create Customers table
CREATE TABLE dev_customers (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- Create Roles table
CREATE TABLE dev_roles (
    id INT PRIMARY KEY,
    role_name VARCHAR(20) UNIQUE NOT NULL,
    role_desc VARCHAR(200)
);

-- Insert default roles
INSERT INTO dev_roles (id, role_name, role_desc)
VALUES
    (1, 'Super user', 'Root user with all access and privileges. Selected few have this role'),
    (2, 'Admin', 'Similar to super user, but can not access all tables'),
    (3, 'Plain', 'Lowest user, can only view');

-- Create Telegram Users table
CREATE TABLE dev_tg_users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    role_id INT REFERENCES dev_roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default Telegram users
INSERT INTO dev_tg_users (telegram_id, role_id)
VALUES
    (5220982261, 1);

-- Create Employees table
CREATE TABLE dev_employees (
    emp_id SERIAL PRIMARY KEY,
    tg_id INT REFERENCES dev_tg_users(id),
    emp_first_name VARCHAR(50),
    emp_last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default employees
INSERT INTO dev_employees (tg_id, emp_first_name, emp_last_name)
VALUES
    (1, 'Alon', 'Margalit');