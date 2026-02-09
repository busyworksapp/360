# Master Admin Quick Reference Card

## 🔐 Login Credentials
- **Email**: donfabio@360degreesupply.co.za
- **Password**: Dot@com12345
- **URL**: /admin/login → /master-admin/dashboard

## 🎯 Quick Actions

### 👥 User Management
| Action | URL | Method |
|--------|-----|--------|
| List Users | `/master-admin/users` | GET |
| Add User | `/master-admin/users/add` | GET/POST |
| Edit User | `/master-admin/users/<id>/edit` | GET/POST |
| View User | `/master-admin/users/<id>` | GET |
| Reset Password | `/master-admin/users/<id>/reset-password` | POST |
| Delete User | `/master-admin/users/<id>/delete` | POST |

### 👨‍💼 Customer Management
| Action | URL | Method |
|--------|-----|--------|
| List Customers | `/master-admin/customers` | GET |
| Edit Customer | `/master-admin/customers/<id>/edit` | GET/POST |
| Delete Customer | `/master-admin/customers/<id>/delete` | POST |

### 📦 Product Management
| Action | URL | Method |
|--------|-----|--------|
| List Products | `/master-admin/products` | GET |
| Delete Product | `/master-admin/products/<id>/delete` | POST |

### 🛒 Order Management
| Action | URL | Method |
|--------|-----|--------|
| List Orders | `/master-admin/orders` | GET |
| Update Status | `/master-admin/orders/<id>/update-status` | POST |
| Delete Order | `/master-admin/orders/<id>/delete` | POST |

### 📄 Invoice Management
| Action | URL | Method |
|--------|-----|--------|
| List Invoices | `/master-admin/invoices` | GET |
| Delete Invoice | `/master-admin/invoices/<id>/delete` | POST |

### 💳 Transaction Management
| Action | URL | Method |
|--------|-----|--------|
| List Transactions | `/master-admin/transactions` | GET |
| Delete Transaction | `/master-admin/transactions/<id>/delete` | POST |

### 🗄️ Database Management
| Action | URL | Method |
|--------|-----|--------|
| List Tables | `/master-admin/database` | GET |
| View Table | `/master-admin/database/<table>` | GET |

### 🔍 Monitoring
| Action | URL | Method |
|--------|-----|--------|
| Audit Logs | `/master-admin/audit-logs` | GET |
| Security Events | `/master-admin/security-events` | GET |
| Resolve Event | `/master-admin/security-events/<id>/resolve` | POST |
| System Logs | `/master-admin/system-logs` | GET |

## 🚨 Important Reminders

### ✅ DO
- ✅ Change default password after first login
- ✅ Review audit logs regularly
- ✅ Confirm before deleting data
- ✅ Use strong passwords (8+ characters)
- ✅ Monitor security events

### ❌ DON'T
- ❌ Delete your own account
- ❌ Share master admin credentials
- ❌ Delete data without confirmation
- ❌ Access database unnecessarily
- ❌ Ignore security alerts

## 📊 Dashboard Stats
- Total Users
- Total Orders
- Total Products
- Security Alerts
- Recent Activities
- System Errors

## 🔒 Security Features
- All actions logged
- IP address tracking
- User agent recording
- Severity levels (info, warning, critical)
- Unauthorized access alerts
- Activity monitoring

## 🆘 Troubleshooting

### Can't Login?
1. Check email: donfabio@360degreesupply.co.za
2. Check password: Dot@com12345
3. Run: `python verify_master_admin_setup.py`

### Access Denied?
1. Verify master_admin profile exists
2. Check is_active = TRUE
3. Review security events

### Missing Features?
1. Check master_admin_routes.py is loaded
2. Verify templates exist
3. Check browser console for errors

## 📞 Support
- Documentation: MASTER_ADMIN_COMPLETE_GUIDE.md
- Implementation: MASTER_ADMIN_IMPLEMENTATION.md
- Setup Script: verify_master_admin_setup.py
