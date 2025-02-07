--CREATE DATABASE myuser;

CREATE DATABASE airflow;
GRANT ALL PRIVILEGES ON DATABASE airflow TO myuser;

DROP TABLE IF EXISTS ${TABLE_ORDERS}, ${TABLE_CUSTOMERS}, ${TABLE_ROLES}, ${TABLE_TG_USERS},
${TABLE_EMPLOYEES}, ${TABLE_CATEGORIES}, ${TABLE_ITEMS}, ${TABLE_FLAT_ORDERS} CASCADE;

CREATE TABLE ${TABLE_CUSTOMERS} (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);


-- Create Roles table
CREATE TABLE ${TABLE_ROLES} (
    id INT PRIMARY KEY,
    role_name VARCHAR(20) UNIQUE NOT NULL,
    role_desc VARCHAR(200)
);

-- Insert default roles
INSERT INTO ${TABLE_ROLES} (id, role_name, role_desc)
VALUES
    (1, 'Super user', 'Root user with all access and privileges. Selected few have this role'),
    (2, 'Admin', 'Similar to super user, but can not access all tables'),
    (3, 'Plain', 'Lowest user, can only view');

-- Create Telegram Users table
CREATE TABLE ${TABLE_TG_USERS} (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    role_id INT REFERENCES dev_roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default Telegram users
INSERT INTO ${TABLE_TG_USERS} (telegram_id, role_id)
VALUES
    (5220982261, 1);

-- Create Employees table
CREATE TABLE ${TABLE_EMPLOYEES} (
    emp_id SERIAL PRIMARY KEY,
    tg_id INT REFERENCES dev_tg_users(id),
    emp_first_name VARCHAR(50),
    emp_last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default employees
INSERT INTO ${TABLE_EMPLOYEES} (tg_id, emp_first_name, emp_last_name)
VALUES
    (1, 'Alon', 'Margalit');


-- Table for Airflow

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS ${TABLE_ORDERS} (
    internal_order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id          BIGINT NOT NULL,
    customer_id       BIGINT NOT NULL,
    order_date        DATE NOT NULL,
    ship_date         DATE,
    order_status      VARCHAR(50),
    items             JSONB,
    inserted_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ${TABLE_FLAT_ORDERS} (
    internal_order_id UUID NOT NULL,
    order_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    order_date DATE NOT NULL,
    ship_date DATE,
    order_status VARCHAR(50),
    category VARCHAR(50),
    product_name VARCHAR(100),
    brand VARCHAR(50),
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Items Data
-- Create categories table
CREATE TABLE IF NOT EXISTS ${TABLE_CATEGORIES} (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE
);

-- Create items table
CREATE TABLE IF NOT EXISTS ${TABLE_ITEMS} (
    item_id SERIAL PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    category_id INT NOT NULL,
    brand VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

-- Insert categories
INSERT INTO ${TABLE_CATEGORIES} (category_name) VALUES
('Electronics'),
('Clothing'),
('Home & Kitchen'),
('Books'),
('Sports & Outdoors'),
('Toys & Games'),
('Automotive'),
('Beauty & Personal Care'),
('Health & Wellness'),
('Groceries'),
('Pet Supplies');

-- Insert items data
INSERT INTO ${TABLE_ITEMS} (product_id, category_id, product_name, brand, price) VALUES
('ELEC-001-DELL', 1, 'Laptop', 'Dell', 999.99),
('ELEC-001-HP', 1, 'Laptop', 'HP', 899.99),
('ELEC-001-LEN', 1, 'Laptop', 'Lenovo', 799.99),
('ELEC-002-SAM', 1, 'Smartphone', 'Samsung', 799.99),
('ELEC-002-APP', 1, 'Smartphone', 'Apple', 999.99),
('ELEC-002-ONE', 1, 'Smartphone', 'OnePlus', 699.99),
('ELEC-003-APP', 1, 'Tablet', 'Apple', 499.99),
('ELEC-003-SAM', 1, 'Tablet', 'Samsung', 399.99),
('ELEC-003-LEN', 1, 'Tablet', 'Lenovo', 299.99),
('ELEC-004-LG', 1, 'Monitor', 'LG', 199.99),
('ELEC-004-DEL', 1, 'Monitor', 'Dell', 249.99),
('ELEC-004-ASU', 1, 'Monitor', 'Asus', 179.99),
('ELEC-005-SON', 1, 'Headphones', 'Sony', 149.99),
('ELEC-005-BOS', 1, 'Headphones', 'Bose', 249.99),
('ELEC-005-JBL', 1, 'Headphones', 'JBL', 99.99),
('CLTH-001-HM', 2, 'T-shirt', 'H&M', 19.99),
('CLTH-001-UNI', 2, 'T-shirt', 'Uniqlo', 14.99),
('CLTH-001-ZAR', 2, 'T-shirt', 'ZARA', 24.99),
('CLTH-002-LEV', 2, 'Jeans', 'Levi''s', 49.99),
('CLTH-002-WRA', 2, 'Jeans', 'Wrangler', 39.99),
('CLTH-002-ZAR', 2, 'Jeans', 'ZARA', 59.99),
('CLTH-003-ZAR', 2, 'Jacket', 'ZARA', 89.99),
('CLTH-003-NF', 2, 'Jacket', 'North Face', 129.99),
('CLTH-003-COL', 2, 'Jacket', 'Columbia', 99.99),
('CLTH-004-NIK', 2, 'Sneakers', 'Nike', 69.99),
('CLTH-004-ADI', 2, 'Sneakers', 'Adidas', 79.99),
('CLTH-004-PUM', 2, 'Sneakers', 'Puma', 59.99),
('CLTH-005-UNI', 2, 'Socks', 'Uniqlo', 9.99),
('CLTH-005-HAN', 2, 'Socks', 'Hanes', 4.99),
('CLTH-005-ADI', 2, 'Socks', 'Adidas', 12.99),
('HOME-001-NIN', 3, 'Blender', 'Ninja', 79.99),
('HOME-001-OST', 3, 'Blender', 'Oster', 69.99),
('HOME-001-BRE', 3, 'Blender', 'Breville', 99.99),
('HOME-002-PAN', 3, 'Microwave', 'Panasonic', 149.99),
('HOME-002-SAM', 3, 'Microwave', 'Samsung', 139.99),
('HOME-002-LG', 3, 'Microwave', 'LG', 129.99),
('HOME-003-DYS', 3, 'Vacuum Cleaner', 'Dyson', 199.99),
('HOME-003-HOO', 3, 'Vacuum Cleaner', 'Hoover', 149.99),
('HOME-003-SHA', 3, 'Vacuum Cleaner', 'Shark', 169.99),
('HOME-004-HON', 3, 'Air Purifier', 'Honeywell', 129.99),
('HOME-004-LEV', 3, 'Air Purifier', 'Levoit', 99.99),
('HOME-004-DYS', 3, 'Air Purifier', 'Dyson', 199.99),
('HOME-005-CUI', 3, 'Toaster', 'Cuisinart', 49.99),
('HOME-005-HAM', 3, 'Toaster', 'Hamilton Beach', 39.99),
('HOME-005-BD', 3, 'Toaster', 'Black+Decker', 29.99),
('BOOK-001-PEN', 4, 'Fiction Novel', 'Penguin', 14.99),
('BOOK-001-HAR', 4, 'Fiction Novel', 'HarperCollins', 12.99),
('BOOK-001-RAN', 4, 'Fiction Novel', 'Random House', 16.99),
('BOOK-002-PEA', 4, 'Science Textbook', 'Pearson', 79.99),
('BOOK-002-MCG', 4, 'Science Textbook', 'McGraw Hill', 89.99),
('BOOK-002-CEN', 4, 'Science Textbook', 'Cengage', 84.99),
('BOOK-003-SIM', 4, 'Biography', 'Simon & Schuster', 19.99),
('BOOK-003-KNO', 4, 'Biography', 'Knopf', 17.99),
('BOOK-003-HAC', 4, 'Biography', 'Hachette', 21.99),
('BOOK-004-ATK', 4, 'Cookbook', 'America''s Test Kitchen', 29.99),
('BOOK-004-TOH', 4, 'Cookbook', 'Taste of Home', 24.99),
('BOOK-004-FN', 4, 'Cookbook', 'Food Network', 19.99),
('BOOK-005-SMP', 4, 'Mystery Thriller', 'St. Martin''s Press', 18.99),
('BOOK-005-BAN', 4, 'Mystery Thriller', 'Bantam', 16.99),
('BOOK-005-ORB', 4, 'Mystery Thriller', 'Orbit', 15.99),
('SPRT-001-WIL', 5, 'Tennis Racket', 'Wilson', 49.99),
('SPRT-001-BAB', 5, 'Tennis Racket', 'Babolat', 69.99),
('SPRT-001-HEA', 5, 'Tennis Racket', 'Head', 59.99),
('SPRT-002-ADI', 5, 'Soccer Ball', 'Adidas', 29.99),
('SPRT-002-NIK', 5, 'Soccer Ball', 'Nike', 27.99),
('SPRT-002-PUM', 5, 'Soccer Ball', 'Puma', 25.99),
('SPRT-003-MAN', 5, 'Yoga Mat', 'Manduka', 39.99),
('SPRT-003-GAI', 5, 'Yoga Mat', 'Gaiam', 29.99),
('SPRT-003-LUL', 5, 'Yoga Mat', 'Lululemon', 49.99),
('SPRT-004-BOW', 5, 'Dumbbells', 'Bowflex', 89.99),
('SPRT-004-CAP', 5, 'Dumbbells', 'CAP Barbell', 79.99),
('SPRT-004-ROG', 5, 'Dumbbells', 'Rogue', 99.99),
('SPRT-005-COL', 5, 'Camping Tent', 'Coleman', 129.99),
('SPRT-005-REI', 5, 'Camping Tent', 'REI', 149.99),
('SPRT-005-BIG', 5, 'Camping Tent', 'Big Agnes', 199.99),
('TOYS-001-HAS', 6, 'Board Game', 'Hasbro', 29.99),
('TOYS-001-MAT', 6, 'Board Game', 'Mattel', 19.99),
('TOYS-001-RAV', 6, 'Board Game', 'Ravensburger', 24.99),
('TOYS-002-MAR', 6, 'Action Figure', 'Marvel', 14.99),
('TOYS-002-DC', 6, 'Action Figure', 'DC', 12.99),
('TOYS-002-HAS', 6, 'Action Figure', 'Hasbro', 16.99),
('TOYS-003-LEG', 6, 'Lego Set', 'LEGO', 49.99),
('TOYS-003-MEG', 6, 'Lego Set', 'Mega Bloks', 39.99),
('TOYS-003-KNE', 6, 'Lego Set', 'K''NEX', 29.99),
('TOYS-004-TRA', 6, 'RC Car', 'Traxxas', 99.99),
('TOYS-004-RED', 6, 'RC Car', 'Redcat', 89.99),
('TOYS-004-ARR', 6, 'RC Car', 'ARRMA', 109.99),
('TOYS-005-TY', 6, 'Stuffed Animal', 'Ty', 9.99),
('TOYS-005-AUR', 6, 'Stuffed Animal', 'Aurora', 12.99),
('TOYS-005-GUN', 6, 'Stuffed Animal', 'Gund', 14.99),
('AUTO-001-COV', 7, 'Car Cover', 'Covercraft', 59.99),
('AUTO-001-OXG', 7, 'Car Cover', 'OxGord', 49.99),
('AUTO-001-DUC', 7, 'Car Cover', 'Duck Covers', 69.99),
('AUTO-002-GAR', 7, 'Dashboard Camera', 'Garmin', 99.99),
('AUTO-002-REX', 7, 'Dashboard Camera', 'Rexing', 89.99),
('AUTO-002-VAN', 7, 'Dashboard Camera', 'Vantrue', 109.99),
('AUTO-003-VIA', 7, 'Tire Inflator', 'Viair', 49.99),
('AUTO-003-KEN', 7, 'Tire Inflator', 'Kensun', 39.99),
('AUTO-003-AUD', 7, 'Tire Inflator', 'Audew', 59.99),
('AUTO-004-MOB', 7, 'Engine Oil', 'Mobil 1', 29.99),
('AUTO-004-CAS', 7, 'Engine Oil', 'Castrol', 24.99),
('AUTO-004-VAL', 7, 'Engine Oil', 'Valvoline', 19.99),
('AUTO-005-CHE', 7, 'Car Wash Kit', 'Chemical Guys', 39.99),
('AUTO-005-MEG', 7, 'Car Wash Kit', 'Meguiar''s', 34.99),
('AUTO-005-ARM', 7, 'Car Wash Kit', 'Armor All', 29.99),
('BEAU-001-PAN', 8, 'Shampoo', 'Pantene', 9.99),
('BEAU-001-HAS', 8, 'Shampoo', 'Head & Shoulders', 8.99),
('BEAU-001-DOV', 8, 'Shampoo', 'Dove', 7.99),
('BEAU-002-OLA', 8, 'Face Cream', 'Olay', 19.99),
('BEAU-002-NEU', 8, 'Face Cream', 'Neutrogena', 18.99),
('BEAU-002-LOR', 8, 'Face Cream', 'L''Oreal', 21.99),
('BEAU-003-MAC', 8, 'Lipstick', 'MAC', 24.99),
('BEAU-003-REV', 8, 'Lipstick', 'Revlon', 19.99),
('BEAU-003-MAY', 8, 'Lipstick', 'Maybelline', 14.99),
('BEAU-004-OPI', 8, 'Nail Polish', 'OPI', 9.99),
('BEAU-004-ESS', 8, 'Nail Polish', 'Essie', 8.99),
('BEAU-004-SAL', 8, 'Nail Polish', 'Sally Hansen', 7.99),
('BEAU-005-AVE', 8, 'Body Lotion', 'Aveeno', 14.99),
('BEAU-005-NIV', 8, 'Body Lotion', 'Nivea', 12.99),
('BEAU-005-JER', 8, 'Body Lotion', 'Jergens', 11.99),
('HLTH-001-NAT', 9, 'Vitamins', 'Nature Made', 14.99),
('HLTH-001-CEN', 9, 'Vitamins', 'Centrum', 16.99),
('HLTH-001-OAD', 9, 'Vitamins', 'One A Day', 13.99),
('HLTH-002-OPN', 9, 'Protein Powder', 'Optimum Nutrition', 29.99),
('HLTH-002-DYM', 9, 'Protein Powder', 'Dymatize', 34.99),
('HLTH-002-MUS', 9, 'Protein Powder', 'MuscleTech', 27.99),
('HLTH-003-MAN', 9, 'Yoga Mat', 'Manduka', 39.99),
('HLTH-003-GAI', 9, 'Yoga Mat', 'Gaiam', 29.99),
('HLTH-003-LUL', 9, 'Yoga Mat', 'Lululemon', 49.99),
('HLTH-004-TRI', 9, 'Foam Roller', 'TriggerPoint', 24.99),
('HLTH-004-AMA', 9, 'Foam Roller', 'AmazonBasics', 19.99),
('HLTH-004-321', 9, 'Foam Roller', '321 STRONG', 29.99),
('HLTH-005-THE', 9, 'Resistance Bands', 'TheraBand', 14.99),
('HLTH-005-FIT', 9, 'Resistance Bands', 'Fit Simplify', 12.99),
('HLTH-005-WHA', 9, 'Resistance Bands', 'Whatafit', 11.99),
('GROC-001-BAR', 10, 'Pasta', 'Barilla', 2.99),
('GROC-001-DEC', 10, 'Pasta', 'De Cecco', 3.49),
('GROC-001-RON', 10, 'Pasta', 'Ronzoni', 2.79),
('GROC-002-DAI', 10, 'Milk', 'DairyPure', 0.99),
('GROC-002-HOR', 10, 'Milk', 'Horizon', 1.49),
('GROC-002-ORG', 10, 'Milk', 'Organic Valley', 1.99),
('GROC-003-STA', 10, 'Coffee', 'Starbucks', 9.99),
('GROC-003-DUN', 10, 'Coffee', 'Dunkin''', 8.99),
('GROC-003-FOL', 10, 'Coffee', 'Folgers', 7.99),
('GROC-004-LAY', 10, 'Snacks', 'Lay''s', 3.49),
('GROC-004-DOR', 10, 'Snacks', 'Doritos', 2.99),
('GROC-004-PRI', 10, 'Snacks', 'Pringles', 2.79),
('GROC-005-TRO', 10, 'Juice', 'Tropicana', 3.99),
('GROC-005-SIM', 10, 'Juice', 'Simply', 3.49),
('GROC-005-MIN', 10, 'Juice', 'Minute Maid', 2.99),
('PETS-001-PED', 11, 'Dog Food', 'Pedigree', 19.99),
('PETS-001-BLU', 11, 'Dog Food', 'Blue Buffalo', 29.99),
('PETS-001-PUR', 11, 'Dog Food', 'Purina', 24.99),
('PETS-002-TID', 11, 'Cat Litter', 'Tidy Cats', 14.99),
('PETS-002-FRE', 11, 'Cat Litter', 'Fresh Step', 13.99),
('PETS-002-ARM', 11, 'Cat Litter', 'Arm & Hammer', 15.99),
('PETS-003-BUR', 11, 'Pet Shampoo', 'Burt''s Bees', 9.99),
('PETS-003-WAH', 11, 'Pet Shampoo', 'Wahl', 8.99),
('PETS-003-EAR', 11, 'Pet Shampoo', 'Earthbath', 12.99),
('PETS-004-MID', 11, 'Pet Bed', 'MidWest Homes', 29.99),
('PETS-004-FUR', 11, 'Pet Bed', 'Furhaven', 39.99),
('PETS-004-KH', 11, 'Pet Bed', 'K&H Pet Products', 49.99),
('PETS-005-KON', 11, 'Chew Toys', 'KONG', 14.99),
('PETS-005-NYL', 11, 'Chew Toys', 'Nylabone', 12.99),
('PETS-005-BEN', 11, 'Chew Toys', 'Benebone', 16.99);