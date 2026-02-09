# Master Admin Advanced Security & Monitoring Guide

## 🚨 Overview

The Master Admin now has complete control over system security, user monitoring, and system operations with advanced features including:

- **IP Blocking**: Block malicious IPs permanently or temporarily
- **System Control**: Shut down or activate the entire system
- **User Permissions**: Control what users can access and see
- **Live Monitoring**: Real-time log monitoring with color-coded severity
- **Deep Dive Logs**: Detailed investigation of individual log entries
- **Analytics**: System usage statistics and insights

## 🔒 IP Blocking & Security

### Block IP Address
**URL**: `/master-admin/security/blocked-ips`

**Features**:
- Block IPs permanently or temporarily
- Set custom block duration (hours)
- Add reason for blocking
- Track block attempts
- View last attempt timestamp

**How to Block**:
1. Click "Block New IP" button
2. Enter IP address (e.g., 192.168.1.1)
3. Enter reason for blocking
4. Choose permanent or temporary
5. Set duration if temporary
6. Click "Block IP"

**Unblock IP**:
- Click "Unblock" button next to blocked IP
- Confirm action
- IP is immediately unblocked

### Automatic Blocking
The system can automatically block IPs that:
- Make too many failed login attempts
- Trigger security events
- Show suspicious behavior patterns

## 🎛️ System Control

### System Shutdown
**URL**: `/master-admin/system/control`

**Features**:
- Shut down entire system
- Only master admins can access during shutdown
- Set shutdown reason
- Track who shut down the system and when

**How to Shutdown**:
1. Go to System Control
2. Click "Shutdown System"
3. Enter shutdown reason
4. Confirm shutdown
5. System is now offline for all users except master admins

**Activate System**:
- Click "Activate System" button
- System is immediately available to all users

### Maintenance Mode
**Features**:
- Put system in maintenance mode
- Display custom message to users
- Less severe than full shutdown
- Users see maintenance page

**How to Enable**:
1. Click "Enable Maintenance"
2. Enter custom message
3. Confirm
4. Users see maintenance page

## 👥 User Permissions Management

### Manage User Permissions
**URL**: `/master-admin/permissions/user/<user_id>`

**Access Control**:
- Can Access Products
- Can Access Services
- Can Access Cart
- Can Access Orders
- Can Access Invoices
- Can Access Transactions
- Can Access Profile

**Sidebar Visibility**:
- Show/Hide Products Tab
- Show/Hide Services Tab
- Show/Hide Orders Tab
- Show/Hide Invoices Tab
- Show/Hide Transactions Tab
- Show/Hide Profile Tab

**Account Blocking**:
- Block user account
- Set block reason
- Track who blocked and when
- Blocked users cannot login

### Manage Customer Permissions
**URL**: `/master-admin/permissions/customer/<customer_id>`

Same features as user permissions but for customers.

## 📊 Detailed Logs & Monitoring

### Log Severity Levels (Color Coded)

#### 🟢 Green (Info)
- Normal operations
- Successful requests
- Regular user activity

#### 🟡 Yellow (Warning)
- Late responses
- Minor issues
- Unusual but not critical activity

#### 🟠 Orange (Error)
- Failed requests
- Application errors
- Issues requiring attention

#### 🔴 Red (Critical)
- System failures
- Security breaches
- Critical errors requiring immediate action

### Detailed Logs
**URL**: `/master-admin/logs/detailed`

**Features**:
- View all system logs
- Filter by type (request, action, error, security)
- Filter by severity (info, warning, error, critical)
- Filter suspicious logs only
- Pagination (100 logs per page)
- Color-coded severity levels

**Log Information**:
- Timestamp
- Severity level
- Log type
- Username
- IP address
- Request path
- Response status
- Response time (ms)
- Suspicious flag

### Deep Dive into Logs
**URL**: `/master-admin/logs/detailed/<log_id>`

**Detailed Information**:

**Basic Info**:
- Timestamp
- Severity
- Log type
- Suspicious flag
- Review status

**User Info**:
- Username
- User ID
- IP address
- Session ID
- Device type
- Browser

**Request Details**:
- HTTP method
- Request path
- Referrer
- User agent
- Request data (POST/PUT)

**Response Details**:
- Status code
- Response time

**Action Details** (if applicable):
- Action performed
- Target table
- Target ID
- Old value
- New value

**Error Details** (if error):
- Error message
- Full traceback

**Review**:
- Mark as reviewed
- Add review notes
- Track reviewer and time

### Live Logs
**URL**: `/master-admin/logs/live`

**Features**:
- Real-time log monitoring
- Auto-refresh every 2 seconds
- Pause/Resume functionality
- Clear logs button
- Filter by severity
- Filter suspicious only
- Shows last 100 logs
- Color-coded rows

**Controls**:
- Pause/Resume updates
- Clear display
- Filter checkboxes
- Live count display
- Connection status

## 📈 Analytics & Insights

**URL**: `/master-admin/analytics`

**Statistics** (Last 24 hours):
- Total requests
- Error requests
- Suspicious requests
- Top 10 IPs by request count
- Top 10 users by activity
- Average response time

## 🚨 Security Features

### Suspicious Activity Detection

Logs are flagged as suspicious when:
- Failed login attempts
- 401/403 responses
- Multiple rapid requests
- Unusual access patterns
- Security event triggers

### Automatic Actions

System automatically:
- Logs all requests
- Tracks response times
- Flags suspicious activity
- Records user actions
- Monitors errors

### Security Best Practices

1. **Regular Monitoring**:
   - Check live logs daily
   - Review suspicious logs
   - Investigate critical errors

2. **IP Management**:
   - Block malicious IPs immediately
   - Review blocked IPs weekly
   - Unblock false positives

3. **User Management**:
   - Review user permissions regularly
   - Block suspicious accounts
   - Monitor user activity

4. **System Control**:
   - Use shutdown only in emergencies
   - Prefer maintenance mode for updates
   - Always provide clear messages

## 🔧 Technical Details

### Database Tables

**blocked_ips**:
- Stores blocked IP addresses
- Tracks block attempts
- Manages expiration

**system_controls**:
- System status
- Maintenance mode
- Shutdown information

**user_permissions**:
- User access control
- Sidebar visibility
- Account blocking

**detailed_logs**:
- Comprehensive request logs
- Error tracking
- User activity monitoring

### API Endpoints

**Live Logs API**:
```
GET /master-admin/api/logs/live?since=<timestamp>
```
Returns logs since timestamp in JSON format.

## 📝 Usage Examples

### Example 1: Block Malicious IP
1. Notice suspicious activity in live logs
2. Click on log to see details
3. Note the IP address
4. Go to Blocked IPs
5. Block the IP with reason
6. Monitor for further attempts

### Example 2: Investigate Error
1. See red (critical) log in live logs
2. Click to view details
3. Review error message and traceback
4. Check user and IP
5. Mark as reviewed with notes
6. Take corrective action

### Example 3: Restrict User Access
1. Go to Users
2. Click on user
3. Click "Manage Permissions"
4. Uncheck access permissions
5. Hide sidebar tabs
6. Save changes
7. User can no longer access restricted areas

### Example 4: Emergency Shutdown
1. Detect critical security issue
2. Go to System Control
3. Click "Shutdown System"
4. Enter reason: "Security breach detected"
5. Confirm shutdown
6. System offline for all except master admins
7. Investigate and fix issue
8. Activate system when safe

## 🎯 Quick Reference

### Color Codes
- 🟢 Green = Good (Info)
- 🟡 Yellow = Caution (Warning)
- 🟠 Orange = Problem (Error)
- 🔴 Red = Critical (Urgent)

### Keyboard Shortcuts
- None currently (future feature)

### Important URLs
- Dashboard: `/master-admin/dashboard`
- Blocked IPs: `/master-admin/security/blocked-ips`
- System Control: `/master-admin/system/control`
- Live Logs: `/master-admin/logs/live`
- Detailed Logs: `/master-admin/logs/detailed`
- Analytics: `/master-admin/analytics`

## ⚠️ Warnings

1. **System Shutdown**: Only use in emergencies
2. **IP Blocking**: Verify IP before blocking
3. **User Blocking**: Provide clear reasons
4. **Permissions**: Don't lock yourself out
5. **Logs**: Review regularly for security

## 🆘 Troubleshooting

**Can't access system after shutdown**:
- Only master admins can access
- Check your master admin status
- Contact another master admin

**Blocked wrong IP**:
- Go to Blocked IPs
- Click Unblock
- IP is immediately accessible

**Logs not updating**:
- Check connection status
- Click Resume if paused
- Refresh page

**User can't access features**:
- Check user permissions
- Verify sidebar visibility
- Check if account is blocked

## 📞 Support

For issues or questions:
- Check audit logs for action history
- Review security events for alerts
- Check system logs for errors
- Contact system administrator

## 🎉 Summary

Master Admin now has:
- ✅ Complete IP blocking control
- ✅ System shutdown capability
- ✅ User permission management
- ✅ Live log monitoring
- ✅ Deep dive investigation
- ✅ Color-coded severity levels
- ✅ Real-time analytics
- ✅ Comprehensive security control

You are now the ultimate system administrator with complete control over security, monitoring, and user management!
