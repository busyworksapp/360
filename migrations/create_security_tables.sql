-- Advanced Security Tables Migration
-- Run this to create all security-related tables

-- 1. Blocked IPs table
CREATE TABLE IF NOT EXISTS blocked_ips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL UNIQUE,
    reason TEXT NOT NULL,
    blocked_by INT,
    blocked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_permanent BOOLEAN DEFAULT FALSE,
    expires_at DATETIME,
    block_count INT DEFAULT 1,
    last_attempt DATETIME,
    notes TEXT,
    FOREIGN KEY (blocked_by) REFERENCES users(id),
    INDEX idx_ip (ip_address),
    INDEX idx_blocked_at (blocked_at)
);

-- 2. System Controls table
CREATE TABLE IF NOT EXISTS system_controls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    is_system_active BOOLEAN DEFAULT TRUE,
    maintenance_mode BOOLEAN DEFAULT FALSE,
    maintenance_message TEXT,
    shutdown_reason TEXT,
    shutdown_by INT,
    shutdown_at DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (shutdown_by) REFERENCES users(id)
);

-- Insert default system control record
INSERT INTO system_controls (is_system_active, maintenance_mode)
SELECT TRUE, FALSE
WHERE NOT EXISTS (SELECT 1 FROM system_controls LIMIT 1);

-- 3. User Permissions table
CREATE TABLE IF NOT EXISTS user_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    customer_id INT UNIQUE,
    can_access_products BOOLEAN DEFAULT TRUE,
    can_access_services BOOLEAN DEFAULT TRUE,
    can_access_cart BOOLEAN DEFAULT TRUE,
    can_access_orders BOOLEAN DEFAULT TRUE,
    can_access_invoices BOOLEAN DEFAULT TRUE,
    can_access_transactions BOOLEAN DEFAULT TRUE,
    can_access_profile BOOLEAN DEFAULT TRUE,
    show_products_tab BOOLEAN DEFAULT TRUE,
    show_services_tab BOOLEAN DEFAULT TRUE,
    show_orders_tab BOOLEAN DEFAULT TRUE,
    show_invoices_tab BOOLEAN DEFAULT TRUE,
    show_transactions_tab BOOLEAN DEFAULT TRUE,
    show_profile_tab BOOLEAN DEFAULT TRUE,
    is_blocked BOOLEAN DEFAULT FALSE,
    block_reason TEXT,
    blocked_by INT,
    blocked_at DATETIME,
    max_order_amount DECIMAL(10, 2),
    requires_approval BOOLEAN DEFAULT FALSE,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (blocked_by) REFERENCES users(id)
);

-- 4. Detailed Logs table
CREATE TABLE IF NOT EXISTS detailed_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    log_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    user_id INT,
    customer_id INT,
    username VARCHAR(120),
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_method VARCHAR(10),
    request_path VARCHAR(500),
    request_data TEXT,
    response_status INT,
    response_time FLOAT,
    action VARCHAR(100),
    target_table VARCHAR(100),
    target_id INT,
    old_value TEXT,
    new_value TEXT,
    error_message TEXT,
    error_traceback TEXT,
    session_id VARCHAR(100),
    referrer VARCHAR(500),
    geo_location VARCHAR(100),
    device_type VARCHAR(50),
    browser VARCHAR(100),
    is_suspicious BOOLEAN DEFAULT FALSE,
    is_reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by INT,
    reviewed_at DATETIME,
    review_notes TEXT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_log_type (log_type),
    INDEX idx_severity (severity),
    INDEX idx_ip (ip_address),
    INDEX idx_timestamp (timestamp),
    INDEX idx_suspicious (is_suspicious)
);

-- Verify tables created
SELECT 
    'blocked_ips' as table_name,
    COUNT(*) as record_count
FROM blocked_ips
UNION ALL
SELECT 
    'system_controls' as table_name,
    COUNT(*) as record_count
FROM system_controls
UNION ALL
SELECT 
    'user_permissions' as table_name,
    COUNT(*) as record_count
FROM user_permissions
UNION ALL
SELECT 
    'detailed_logs' as table_name,
    COUNT(*) as record_count
FROM detailed_logs;
