-- Master Admin Setup SQL Script
-- Run this in your MySQL database

-- 1. Create master_admins table
CREATE TABLE IF NOT EXISTS master_admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(32),
    last_login DATETIME,
    last_ip VARCHAR(45),
    granted_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 2. Create user if not exists (donfabio@360degreesupply.co.za)
-- Password hash for: Dot@com12345
INSERT INTO users (email, password_hash, is_admin, created_at)
SELECT 'donfabio@360degreesupply.co.za', 
       'scrypt:32768:8:1$YourHashHere$...', 
       TRUE, 
       NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'donfabio@360degreesupply.co.za'
);

-- 3. Promote user to Master Admin
INSERT INTO master_admins (user_id, is_active, granted_by, created_at)
SELECT u.id, TRUE, u.id, NOW()
FROM users u
WHERE u.email = 'donfabio@360degreesupply.co.za'
AND NOT EXISTS (
    SELECT 1 FROM master_admins ma WHERE ma.user_id = u.id
);

-- Verify setup
SELECT u.id, u.email, u.is_admin, ma.is_active as master_admin_active
FROM users u
LEFT JOIN master_admins ma ON u.id = ma.user_id
WHERE u.email = 'donfabio@360degreesupply.co.za';
