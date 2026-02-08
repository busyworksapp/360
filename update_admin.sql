-- Update Admin Email to Real Address
-- Run this in MySQL Workbench or command line

-- Update first admin account
UPDATE users 
SET email = 'support@360degreesupply.co.za'
WHERE id = 1;

-- Delete second admin account (duplicate)
DELETE FROM users WHERE id = 2;

-- Verify the change
SELECT id, email, is_admin, created_at FROM users WHERE is_admin = 1;
