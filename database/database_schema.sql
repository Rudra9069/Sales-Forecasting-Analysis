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


INSERT INTO products (name, description, category, brand, price, stock_quantity, image_url, rating) VALUES
('Samsung Galaxy S24 Ultra', 'Latest 5G smartphone with 6.8 inch Dynamic AMOLED 2X display, 200MP camera, 12GB RAM, and 256GB storage. Features advanced AI processing and all-day 5000mAh battery.', 'Smartphones', 'Samsung', 74999.00, 100, '/static/images/products/samsung_galaxy_s24_ultra.png', 4.50),
('Apple MacBook Air M3', 'Ultra-thin 15 inch Liquid Retina display laptop with Apple M3 chip, 16GB unified memory, 512GB SSD, and 18-hour battery life. Perfect for professionals and creators.', 'Laptops', 'Apple', 134900.00, 50, '/static/images/products/apple_macbook_air_m3.png', 4.80),
('Sony WF-1000XM5', 'Premium wireless earbuds with industry-leading noise cancellation, LDAC Hi-Res Audio, 24-hour battery life with case, and IPX4 water resistance. Crystal clear call quality.', 'Audio', 'Sony', 19990.00, 200, '/static/images/products/sony_wf_1000xm5.png', 4.20),
('Apple Watch Series 9', 'Advanced smartwatch with Always-On Retina LTPO OLED display, blood oxygen monitoring, ECG, crash detection, 18-hour battery life, and 100+ workout modes.', 'Wearables', 'Apple', 41900.00, 150, '/static/images/products/apple_watch_series_9.png', 4.30),
('Apple iPad Air M2', '11 inch premium tablet with Apple M2 chip, 8GB RAM, 128GB storage, quad speakers, Apple Pencil Pro support, and 60Hz Liquid Retina display.', 'Tablets', 'Apple', 59900.00, 80, '/static/images/products/apple_ipad_air_m2.png', 4.60),
('Apple iPhone 15 Pro Max', 'Titanium design, A17 Pro chip, 48MP main camera, 5x optical zoom, 6.7-inch Super Retina XDR display.', 'Smartphones', 'Apple', 159900.00, 120, '/static/images/products/apple_iphone_15_pro_max.png', 4.80),
('Google Pixel 8 Pro', 'Google Tensor G3, advanced AI features, 50MP main camera, 6.7-inch Super Actua display, 7 years of updates.', 'Smartphones', 'Google', 106999.00, 90, '/static/images/products/google_pixel_8_pro.png', 4.60),
('OnePlus 12', 'Snapdragon 8 Gen 3, Hasselblad Camera for Mobile, 5400mAh battery, 100W fast charging, 6.82-inch AMOLED.', 'Smartphones', 'OnePlus', 64999.00, 150, '/static/images/products/oneplus_12.png', 4.50),
('Xiaomi 14 Ultra', 'Leica Summilux optical lenses, 1-inch sensor, Snapdragon 8 Gen 3, 6.73-inch AMOLED, 90W fast charging.', 'Smartphones', 'Xiaomi', 99999.00, 60, '/static/images/products/xiaomi_14_ultra.png', 4.70),
('Vivo X100 Pro', 'Zeiss optics, MediaTek Dimensity 9300, 50MP main camera with 1-inch sensor, 5400mAh battery, 100W charging.', 'Smartphones', 'Vivo', 89999.00, 80, '/static/images/products/vivo_x100_pro.png', 4.60),
('Dell XPS 15', '15.6-inch OLED touch display, Intel Core i7-13700H, NVIDIA RTX 4050, 16GB RAM, 1TB SSD, premium build.', 'Laptops', 'Dell', 185000.00, 45, '/static/images/products/dell_xps_15.png', 4.70),
('Lenovo ThinkPad X1 Carbon', 'Ultralight business laptop, Intel Core i7, 16GB RAM, 512GB SSD, legendary keyboard, robust security.', 'Laptops', 'Lenovo', 165000.00, 70, '/static/images/products/lenovo_thinkpad_x1_carbon.png', 4.90),
('HP Spectre x360', '2-in-1 convertible, 13.5-inch OLED, Intel Core i7, 16GB RAM, 1TB SSD, includes active pen.', 'Laptops', 'HP', 145000.00, 55, '/static/images/products/hp_spectre_x360.png', 4.60),
('ASUS ROG Zephyrus G14', 'Powerful gaming laptop, AMD Ryzen 9, NVIDIA RTX 4060, 14-inch 165Hz display, AniMe Matrix.', 'Laptops', 'ASUS', 155000.00, 65, '/static/images/products/asus_rog_zephyrus_g14.png', 4.80),
('Microsoft Surface Laptop 5', 'Sleek and light, 15-inch PixelSense display, Intel Core i7, 16GB RAM, 512GB SSD, great battery life.', 'Laptops', 'Microsoft', 125000.00, 85, '/static/images/products/microsoft_surface_laptop_5.png', 4.50),
('Apple AirPods Pro 2', 'Active Noise Cancellation, Adaptive Audio, Personalized Spatial Audio, MagSafe charging case.', 'Audio', 'Apple', 24900.00, 250, '/static/images/products/apple_airpods_pro_2.png', 4.80),
('Bose QuietComfort Ultra', 'World-class noise cancellation, spatial audio, up to 24 hours battery life, premium comfort.', 'Audio', 'Bose', 25900.00, 180, '/static/images/products/bose_quietcomfort_ultra.png', 4.70),
('Sennheiser Momentum 4', 'Exceptional sound quality, adaptive noise cancellation, up to 60 hours battery life, comfortable fit.', 'Audio', 'Sennheiser', 22990.00, 120, '/static/images/products/sennheiser_momentum_4.png', 4.60),
('Jabra Elite 10', 'Comfortable fit, advanced active noise cancellation, spatial sound with Dolby Head Tracking, multipoint.', 'Audio', 'Jabra', 18999.00, 140, '/static/images/products/jabra_elite_10.png', 4.40),
('Samsung Galaxy Buds2 Pro', 'Intelligent Active Noise Cancellation, 24-bit Hi-Fi audio, 360 audio, seamless Samsung integration.', 'Audio', 'Samsung', 15999.00, 210, '/static/images/products/samsung_galaxy_buds2_pro.png', 4.50),
('Garmin Fenix 7X Pro', 'Multisport GPS watch, built-in flashlight, solar charging, advanced training metrics, rugged design.', 'Wearables', 'Garmin', 85990.00, 40, '/static/images/products/garmin_fenix_7x_pro.png', 4.90),
('Samsung Galaxy Watch 6 Classic', 'Rotating bezel, sapphire crystal display, comprehensive health monitoring, sleep coaching.', 'Wearables', 'Samsung', 36999.00, 160, '/static/images/products/samsung_galaxy_watch_6_classic.jpg', 4.60),
('Fitbit Sense 2', 'Advanced health and fitness smartwatch, ECG, stress tracking, built-in GPS, 6+ days battery.', 'Wearables', 'Fitbit', 24999.00, 130, '/static/images/products/fitbit_sense_2.jpg', 4.30),
('Amazfit GTR 4', '14-day battery life, dual-band GPS, 150+ sports modes, BioTracker 4.0 health data sensor.', 'Wearables', 'Amazfit', 16999.00, 180, '/static/images/products/amazfit_gtr_4.jpg', 4.20),
('Google Pixel Watch 2', 'Advanced Fitbit health and fitness tracking, safety features, fast performance, 24-hour battery with AOD.', 'Wearables', 'Google', 39900.00, 90, '/static/images/products/google_pixel_watch_2.jpg', 4.40),
('Samsung Galaxy Tab S9 Ultra', 'Massive 14.6-inch Dynamic AMOLED 2X, Snapdragon 8 Gen 2, S Pen included, IP68 water resistant.', 'Tablets', 'Samsung', 108999.00, 60, '/static/images/products/samsung_galaxy_tab_s9_ultra.jpg', 4.80),
('Microsoft Surface Pro 9', 'Tablet to laptop versatility, Intel Core i5, 8GB RAM, 256GB SSD, 13-inch PixelSense touchscreen.', 'Tablets', 'Microsoft', 98900.00, 75, '/static/images/products/microsoft_surface_pro_9.jpg', 4.60),
('Lenovo Tab P12 Pro', '12.6-inch AMOLED display, Snapdragon 870, Precision Pen 3 included, great for media and light work.', 'Tablets', 'Lenovo', 55000.00, 110, '/static/images/products/lenovo_tab_p12_pro.jpg', 4.50),
('OnePlus Pad', '11.61-inch 144Hz ReadFit display, Dimensity 9000, 9510mAh battery, 67W fast charging, sleek design.', 'Tablets', 'OnePlus', 37999.00, 140, '/static/images/products/oneplus_pad.jpg', 4.40),
('Xiaomi Pad 6', '11-inch 144Hz display, Snapdragon 870, 8840mAh battery, quad speakers with Dolby Atmos.', 'Tablets', 'Xiaomi', 26999.00, 200, '/static/images/products/xiaomi_pad_6.jpg', 4.60);


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
