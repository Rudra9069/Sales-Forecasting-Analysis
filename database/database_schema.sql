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

-- TABLE 3: ORDERS
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
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

-- TABLE 4: ORDER_ITEMS
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- TABLE 5: PAYMENTS
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method ENUM('UPI','card','COD') NOT NULL,
    payment_status ENUM('success','failed','pending') NOT NULL DEFAULT 'pending',
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(12,2) NOT NULL CHECK (amount >= 0),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- TABLE 6: COMPLAINTS
CREATE TABLE complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_id INT NOT NULL,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('open','resolved') NOT NULL DEFAULT 'open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) 
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
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    reason TEXT NOT NULL,
    status ENUM('requested','approved','rejected') NOT NULL DEFAULT 'requested',
    return_date DATE DEFAULT (CURRENT_DATE),
    refund_amount DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) 
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
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_payments_status ON payments(payment_status);

-- ==============================================================================
-- 9. CREATE SQL VIEWS
-- ==============================================================================

-- Sales Summary
CREATE VIEW vw_sales_summary AS
SELECT 
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_revenue,
    AVG(o.total_amount) AS average_order_value
FROM orders o
WHERE o.status IN ('shipped', 'delivered');

-- Monthly Sales
CREATE VIEW vw_monthly_sales AS
SELECT 
    YEAR(order_date) AS order_year,
    MONTH(order_date) AS order_month,
    SUM(total_amount) AS monthly_revenue,
    COUNT(order_id) AS orders_count
FROM orders
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
    SUM(oi.quantity) AS total_units_sold,
    SUM(oi.quantity * oi.price) AS total_revenue_generated,
    p.rating AS current_rating
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status != 'cancelled'
GROUP BY p.product_id;

-- Customer Purchase History
CREATE VIEW vw_customer_purchase_history AS
SELECT 
    u.user_id,
    u.name,
    u.email,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_spent
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id AND o.status != 'cancelled'
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
    OUT p_order_id INT
)
BEGIN
    INSERT INTO orders (user_id, total_amount, status, shipping_address) 
    VALUES (p_user_id, p_total_amount, 'pending', p_shipping_address);
    SET p_order_id = LAST_INSERT_ID();
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
    IN p_order_id INT,
    IN p_subject VARCHAR(255),
    IN p_description TEXT
)
BEGIN
    INSERT INTO complaints (user_id, order_id, subject, description) 
    VALUES (p_user_id, p_order_id, p_subject, p_description);
END //

DELIMITER ;

-- ==============================================================================
-- 11. CREATE TRIGGERS
-- ==============================================================================
DELIMITER //

-- Reduce stock after order (When an item is added to order_items)
CREATE TRIGGER trg_reduce_stock_after_order
AFTER INSERT ON order_items
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
        -- Retrieve the quantity from order_items
        UPDATE products p
        JOIN order_items oi ON p.product_id = oi.product_id
        SET p.stock_quantity = p.stock_quantity + oi.quantity
        WHERE oi.order_id = NEW.order_id 
        AND oi.product_id = NEW.product_id;
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
