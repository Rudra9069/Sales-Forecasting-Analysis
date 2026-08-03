-- ==============================================================================
-- 1. CREATE DATABASE & CONFIGURATION
-- ==============================================================================
CREATE DATABASE IF NOT EXISTS sales_forecasting_db
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE sales_forecasting_db;

-- ==============================================================================
-- 3. CREATE TABLES (In order of dependencies)
-- ==============================================================================

-- TABLE 1: USERS
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    role ENUM('user','admin') NOT NULL DEFAULT 'user'
) ENGINE=InnoDB;

-- TABLE 2: PRODUCTS
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    brand VARCHAR(100),
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    stock_quantity INT DEFAULT 0 CHECK (stock_quantity >= 0),
    image_url VARCHAR(500),
    rating DECIMAL(3,2) DEFAULT 0.00 CHECK (rating BETWEEN 0 AND 5),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- TABLE 3: TRANSACTIONS (Orders)
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL CHECK (total_amount >= 0),
    status ENUM('pending','shipped','delivered','cancelled') NOT NULL DEFAULT 'pending',
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivery_date DATE,
    shipping_address TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- TABLE 4: TRANSACTION_ITEMS
CREATE TABLE transaction_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- TABLE 5: PAYMENTS
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    payment_method ENUM('UPI','card','COD') NOT NULL,
    payment_status ENUM('success','failed','pending') NOT NULL DEFAULT 'pending',
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(12,2) NOT NULL CHECK (amount >= 0),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- TABLE 6: COMPLAINTS
CREATE TABLE complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    transaction_id INT NOT NULL,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('open','resolved') NOT NULL DEFAULT 'open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- TABLE 7: FEEDBACK
CREATE TABLE feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- TABLE 8: RETURNS
CREATE TABLE returns (
    return_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    product_id INT NOT NULL,
    reason TEXT NOT NULL,
    status ENUM('requested','approved','rejected') NOT NULL DEFAULT 'requested',
    return_date DATE DEFAULT (CURRENT_DATE),
    refund_amount DECIMAL(10,2),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ==============================================================================
-- 5. CREATE INDEXES (For Performance Optimization)
-- ==============================================================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_transactions_order_date ON transactions(order_date);
CREATE INDEX idx_payments_status ON payments(payment_status);


-- ==============================================================================
-- 8. SAMPLE DATA INSERTS (5 records per table)
-- ==============================================================================
INSERT INTO users (name, email, password, phone, address, city, state, pincode, role) VALUES
('John Doe', 'john@example.com', 'hashed_pwd_1', '9876543210', '123 Main St', 'Mumbai', 'MH', '400001', 'user'),
('Jane Smith', 'jane@example.com', 'hashed_pwd_2', '9876543211', '456 Elm St', 'Delhi', 'DL', '110001', 'user'),
('Alice Brown', 'alice@example.com', 'hashed_pwd_3', '9876543212', '789 Oak St', 'Bangalore', 'KA', '560001', 'admin'),
('Bob Davis', 'bob@example.com', 'hashed_pwd_4', '9876543213', '101 Pine St', 'Chennai', 'TN', '600001', 'user'),
('Charlie Evans', 'charlie@example.com', 'hashed_pwd_5', '9876543214', '202 Maple St', 'Pune', 'MH', '411001', 'user');

INSERT INTO products (name, description, category, brand, price, stock_quantity, rating) VALUES
('Smartphone X', 'Latest 5G smartphone', 'Electronics', 'BrandA', 699.99, 100, 4.5),
('Laptop Pro', 'High performance laptop for pros', 'Electronics', 'BrandB', 1299.99, 50, 4.8),
('Wireless Earbuds', 'Noise cancelling earbuds', 'Accessories', 'BrandA', 149.99, 200, 4.2),
('Running Shoes', 'Lightweight comfortable shoes', 'Footwear', 'BrandC', 89.99, 150, 4.0),
('Coffee Maker', 'Automatic espresso machine', 'Home Appliances', 'BrandD', 199.99, 30, 4.6);

INSERT INTO transactions (user_id, total_amount, status, shipping_address, order_date) VALUES
(1, 699.99, 'delivered', '123 Main St, Mumbai, MH 400001', '2023-10-01 10:00:00'),
(2, 1449.98, 'shipped', '456 Elm St, Delhi, DL 110001', '2023-10-02 11:30:00'),
(4, 149.99, 'pending', '101 Pine St, Chennai, TN 600001', '2023-10-05 14:15:00'),
(5, 89.99, 'delivered', '202 Maple St, Pune, MH 411001', '2023-10-08 09:45:00'),
(1, 199.99, 'cancelled', '123 Main St, Mumbai, MH 400001', '2023-10-10 16:20:00');

INSERT INTO transaction_items (transaction_id, product_id, quantity, price) VALUES
(1, 1, 1, 699.99),
(2, 2, 1, 1299.99),
(2, 3, 1, 149.99),
(3, 3, 1, 149.99),
(4, 4, 1, 89.99),
(5, 5, 1, 199.99);

INSERT INTO payments (transaction_id, payment_method, payment_status, amount) VALUES
(1, 'UPI', 'success', 699.99),
(2, 'card', 'success', 1449.98),
(3, 'COD', 'pending', 149.99),
(4, 'UPI', 'success', 89.99),
(5, 'card', 'failed', 199.99);

INSERT INTO complaints (user_id, transaction_id, subject, description, status) VALUES
(1, 1, 'Delivery Delay', 'Package arrived two days later than expected.', 'resolved'),
(4, 3, 'Order Stuck', 'Order has been pending for three days.', 'open'),
(5, 4, 'Wrong Size', 'The shoes received are size 9, requested size 10.', 'open'),
(1, 5, 'Payment Deducted', 'Order cancelled but amount deducted from card.', 'open'),
(2, 2, 'Packaging Damaged', 'Outer box was slightly torn, product inside is fine.', 'resolved');

INSERT INTO feedback (user_id, product_id, rating, comment) VALUES
(1, 1, 5, 'Excellent phone, completely satisfied!'),
(2, 2, 5, 'Best laptop I have ever used.'),
(2, 3, 4, 'Good sound quality but battery could be better.'),
(5, 4, 3, 'Comfortable but wrong size delivered initially.'),
(1, 1, 4, 'Good phone, slightly overpriced.');

INSERT INTO returns (transaction_id, product_id, reason, status, refund_amount) VALUES
(4, 4, 'Wrong size delivered', 'approved', 89.99),
(1, 1, 'Defective screen', 'requested', 699.99),
(2, 3, 'Changed my mind', 'rejected', 0.00),
(5, 5, 'Order was cancelled before shipment', 'approved', 199.99),
(2, 2, 'Keyboard not working', 'requested', 1299.99);


-- ==============================================================================
-- 9. CREATE SQL VIEWS
-- ==============================================================================

-- Sales Summary
CREATE VIEW vw_sales_summary AS
SELECT 
    COUNT(t.transaction_id) AS total_orders,
    SUM(t.total_amount) AS total_revenue,
    AVG(t.total_amount) AS average_order_value
FROM transactions t
WHERE t.status IN ('shipped', 'delivered');

-- Monthly Sales
CREATE VIEW vw_monthly_sales AS
SELECT 
    YEAR(order_date) AS order_year,
    MONTH(order_date) AS order_month,
    SUM(total_amount) AS monthly_revenue,
    COUNT(transaction_id) AS orders_count
FROM transactions
WHERE status IN ('shipped', 'delivered')
GROUP BY YEAR(order_date), MONTH(order_date)
ORDER BY order_year DESC, order_month DESC;

-- Product Performance
CREATE VIEW vw_product_performance AS
SELECT 
    p.product_id,
    p.name,
    p.category,
    p.brand,
    SUM(ti.quantity) AS total_units_sold,
    SUM(ti.quantity * ti.price) AS total_revenue_generated,
    p.rating AS current_rating
FROM products p
LEFT JOIN transaction_items ti ON p.product_id = ti.product_id
LEFT JOIN transactions t ON ti.transaction_id = t.transaction_id AND t.status != 'cancelled'
GROUP BY p.product_id;

-- Customer Purchase History
CREATE VIEW vw_customer_purchase_history AS
SELECT 
    u.user_id,
    u.name,
    u.email,
    COUNT(t.transaction_id) AS total_orders,
    SUM(t.total_amount) AS total_spent
FROM users u
LEFT JOIN transactions t ON u.user_id = t.user_id AND t.status != 'cancelled'
GROUP BY u.user_id;

-- Payment Report
CREATE VIEW vw_payment_report AS
SELECT 
    payment_method,
    payment_status,
    COUNT(payment_id) AS total_transactions,
    SUM(amount) AS total_amount
FROM payments
GROUP BY payment_method, payment_status;


-- ==============================================================================
-- 10. CREATE STORED PROCEDURES
-- ==============================================================================
DELIMITER //

CREATE PROCEDURE PlaceOrder(
    IN p_user_id INT,
    IN p_total_amount DECIMAL(12,2),
    IN p_shipping_address TEXT,
    OUT p_transaction_id INT
)
BEGIN
    INSERT INTO transactions (user_id, total_amount, status, shipping_address) 
    VALUES (p_user_id, p_total_amount, 'pending', p_shipping_address);
    SET p_transaction_id = LAST_INSERT_ID();
END //

CREATE PROCEDURE AddProduct(
    IN p_name VARCHAR(200),
    IN p_description TEXT,
    IN p_category VARCHAR(100),
    IN p_brand VARCHAR(100),
    IN p_price DECIMAL(10,2),
    IN p_stock_quantity INT,
    IN p_image_url VARCHAR(500)
)
BEGIN
    INSERT INTO products (name, description, category, brand, price, stock_quantity, image_url) 
    VALUES (p_name, p_description, p_category, p_brand, p_price, p_stock_quantity, p_image_url);
END //

CREATE PROCEDURE RegisterUser(
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(150),
    IN p_password VARCHAR(255),
    IN p_phone VARCHAR(15)
)
BEGIN
    INSERT INTO users (name, email, password, phone) 
    VALUES (p_name, p_email, p_password, p_phone);
END //

CREATE PROCEDURE SubmitComplaint(
    IN p_user_id INT,
    IN p_transaction_id INT,
    IN p_subject VARCHAR(255),
    IN p_description TEXT
)
BEGIN
    INSERT INTO complaints (user_id, transaction_id, subject, description) 
    VALUES (p_user_id, p_transaction_id, p_subject, p_description);
END //

DELIMITER ;


-- ==============================================================================
-- 11. CREATE TRIGGERS
-- ==============================================================================
DELIMITER //

-- Reduce stock after order (When an item is added to transaction_items)
CREATE TRIGGER trg_reduce_stock_after_order
AFTER INSERT ON transaction_items
FOR EACH ROW
BEGIN
    UPDATE products 
    SET stock_quantity = stock_quantity - NEW.quantity 
    WHERE product_id = NEW.product_id;
END //

-- Restore stock after approved return
CREATE TRIGGER trg_restore_stock_on_return
AFTER UPDATE ON returns
FOR EACH ROW
BEGIN
    IF NEW.status = 'approved' AND OLD.status != 'approved' THEN
        -- Retrieve the quantity from transaction_items
        UPDATE products p
        JOIN transaction_items ti ON p.product_id = ti.product_id
        SET p.stock_quantity = p.stock_quantity + ti.quantity
        WHERE ti.transaction_id = NEW.transaction_id 
        AND ti.product_id = NEW.product_id;
    END IF;
END //

-- Automatically update product average rating after feedback
CREATE TRIGGER trg_update_product_rating
AFTER INSERT ON feedback
FOR EACH ROW
BEGIN
    DECLARE new_avg DECIMAL(3,2);
    
    SELECT AVG(rating) INTO new_avg 
    FROM feedback 
    WHERE product_id = NEW.product_id;
    
    UPDATE products 
    SET rating = new_avg 
    WHERE product_id = NEW.product_id;
END //

DELIMITER ;
