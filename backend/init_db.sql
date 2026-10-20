-- Khởi tạo Database
CREATE DATABASE IF NOT EXISTS doan_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE doan_db;

-- Tạo bảng users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'employee',
    branch_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_users_email (email),
    INDEX ix_users_branch_id (branch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tạo bảng data_sources
CREATE TABLE IF NOT EXISTS data_sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    config JSON NOT NULL,
    column_mapping JSON NOT NULL,
    branch_id VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_data_sources_branch_id (branch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tạo bảng normalized_orders
CREATE TABLE IF NOT EXISTS normalized_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(100) NOT NULL UNIQUE,
    order_date DATE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity FLOAT NOT NULL,
    unit_price FLOAT NOT NULL,
    total_amount FLOAT NOT NULL,
    customer_name VARCHAR(255),
    branch_id VARCHAR(100) NOT NULL,
    source_sheet VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_normalized_orders_order_id (order_id),
    INDEX ix_normalized_orders_order_date (order_date),
    INDEX ix_normalized_orders_product_name (product_name),
    INDEX ix_normalized_orders_branch_id (branch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tạo bảng reports
CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_name VARCHAR(255) NOT NULL,
    period_type VARCHAR(50) NOT NULL,
    period_value VARCHAR(100) NOT NULL,
    branch_id VARCHAR(50) NULL,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    data JSON NULL,
    file_url_excel VARCHAR(255) NULL,
    file_url_pdf VARCHAR(255) NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX ix_reports_branch_id (branch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Chèn sẵn 1 tài khoản Admin mặc định (mật khẩu: admin123)
-- (Lưu ý: Mật khẩu này đã được băm bằng thuật toán bcrypt)
INSERT INTO users (email, hashed_password, full_name, role, branch_id) 
VALUES (
    'admin@example.com', 
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 
    'System Administrator', 
    'admin', 
    NULL
) ON DUPLICATE KEY UPDATE email=email;
