# Master Admin Complete Functions Guide

## Overview
The Master Admin has complete control over all system data and users with full CRUD (Create, Read, Update, Delete) capabilities.

## Access
- URL: `/master-admin/dashboard`
- Only users with master_admin profile can access these functions
- All actions are logged in audit logs for security

## User Management

### View All Users
- **URL**: `/master-admin/users`
- **Features**: 
  - View all system users (admins and customers)
  - Paginated list with 50 users per page
  - See user role, email, and creation date

### Add New User
- **URL**: `/master-admin/users/add`
- **Features**:
  - Create new admin or regular users
  - Set email and password
  - Assign admin privileges
  - Password must be minimum 8 characters

### Edit User
- **URL**: `/master-admin/users/<user_id>/edit`
- **Features**:
  - Update user email
  - Change admin status
  - All changes are logged

### View User Details
- **URL**: `/master-admin/users/<user_id>`
- **Features**:
  - View complete user information
  - See recent activities (last 50)
  - View security events
  - Access to edit, reset password, and delete

### Reset User Password
- **URL**: `/master-admin/users/<user_id>/reset-password` (POST)
- **Features**:
  - Reset any user's password
  - Minimum 8 characters required
  - Action is logged for security

### Delete User
- **URL**: `/master-admin/users/<user_id>/delete` (POST)
- **Features**:
  - Permanently delete user account
  - Cannot delete your own account
  - Action is logged with high severity

## Customer Management

### View All Customers
- **URL**: `/master-admin/customers`
- **Features**:
  - View all registered customers
  - See customer status (active/inactive)
  - View company and contact information
  - Paginated list with 50 customers per page

### Edit Customer
- **URL**: `/master-admin/customers/<customer_id>/edit`
- **Features**:
  - Update customer information
  - Change email, name, phone, company
  - Toggle active status
  - All changes are logged

### Delete Customer
- **URL**: `/master-admin/customers/<customer_id>/delete` (POST)
- **Features**:
  - Permanently delete customer account
  - Removes all associated data
  - Action is logged with warning severity

## Product Management

### View All Products
- **URL**: `/master-admin/products`
- **Features**:
  - View all products in system
  - See pricing in both ZAR and USD
  - View product status and category
  - Paginated list with 50 products per page

### Delete Product
- **URL**: `/master-admin/products/<product_id>/delete` (POST)
- **Features**:
  - Permanently delete product
  - Action is logged with warning severity

## Order Management

### View All Orders
- **URL**: `/master-admin/orders`
- **Features**:
  - View all customer orders
  - See order status and payment status
  - View customer and total amount
  - Paginated list with 50 orders per page

### Update Order Status
- **URL**: `/master-admin/orders/<order_id>/update-status` (POST)
- **Features**:
  - Change order status (pending, processing, shipped, delivered, cancelled)
  - Instant update via dropdown
  - All changes are logged

### Delete Order
- **URL**: `/master-admin/orders/<order_id>/delete` (POST)
- **Features**:
  - Permanently delete order
  - Action is logged with critical severity
  - Confirmation required

## Invoice Management

### View All Invoices
- **URL**: `/master-admin/invoices`
- **Features**:
  - View all invoices in system
  - See invoice status and amounts
  - View due dates and payment status
  - Paginated list with 50 invoices per page

### Delete Invoice
- **URL**: `/master-admin/invoices/<invoice_id>/delete` (POST)
- **Features**:
  - Permanently delete invoice
  - Action is logged with critical severity
  - Confirmation required

## Transaction Management

### View All Transactions
- **URL**: `/master-admin/transactions`
- **Features**:
  - View all payment transactions
  - See payment method and reference
  - View transaction status and amounts
  - Paginated list with 50 transactions per page

### Delete Transaction
- **URL**: `/master-admin/transactions/<transaction_id>/delete` (POST)
- **Features**:
  - Permanently delete transaction record
  - Action is logged with critical severity
  - Confirmation required

## Database Management

### View Database Tables
- **URL**: `/master-admin/database`
- **Features**:
  - View all database tables
  - Access to raw table data
  - Action is logged with warning severity

### View Table Data
- **URL**: `/master-admin/database/<table_name>`
- **Features**:
  - View first 100 rows of any table
  - See all columns and data
  - Action is logged with warning severity

## Security & Monitoring

### Audit Logs
- **URL**: `/master-admin/audit-logs`
- **Features**:
  - View all system audit logs
  - See user actions and changes
  - Paginated list with 100 logs per page

### Security Events
- **URL**: `/master-admin/security-events`
- **Features**:
  - View unresolved security events
  - See event severity and type
  - Resolve security events
  - Paginated list with 50 events per page

### Resolve Security Event
- **URL**: `/master-admin/security-events/<event_id>/resolve` (POST)
- **Features**:
  - Mark security event as resolved
  - Records who resolved it and when
  - Action is logged

### System Logs
- **URL**: `/master-admin/system-logs`
- **Features**:
  - View system error and info logs
  - See log level and messages
  - Paginated list with 100 logs per page

## Security Features

### Audit Trail
- All master admin actions are logged
- Includes user ID, action, timestamp, IP address
- Old and new values recorded for updates
- Severity levels: info, warning, critical

### Access Control
- Only users with active master_admin profile can access
- Unauthorized access attempts are logged
- Cannot delete own account
- All sensitive actions require confirmation

### Activity Monitoring
- User activities tracked
- Security events monitored
- System errors logged
- Real-time dashboard statistics

## Best Practices

1. **User Management**
   - Always verify user identity before resetting passwords
   - Use strong passwords (minimum 8 characters)
   - Regularly review user accounts

2. **Data Management**
   - Confirm before deleting any data
   - Review audit logs regularly
   - Monitor security events

3. **Security**
   - Resolve security events promptly
   - Review system logs for errors
   - Monitor unauthorized access attempts

4. **Database Access**
   - Use database management sparingly
   - Only access when necessary
   - All database views are logged

## Dashboard Statistics

The master admin dashboard shows:
- Total users in system
- Total orders
- Total products
- Unresolved security alerts
- Recent security events
- Recent audit logs
- Recent system errors

## Quick Actions

From the dashboard, you can quickly access:
- User management
- Customer management
- Product management
- Order management
- Invoice management
- Transaction management
- Database management
- Audit logs
- Security events
- System logs

## Support

For issues or questions:
1. Check audit logs for action history
2. Review security events for alerts
3. Check system logs for errors
4. Contact system administrator if needed
