# Smart Locker System - Enhanced Logging System

## Overview

The Smart Locker System now includes a comprehensive logging system that tracks all user activities, authentication events, and administrative actions for security, compliance, and debugging purposes.

## Database Schema

### Log Table Structure

```sql
CREATE TABLE log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user(id),
    item_id INTEGER REFERENCES item(id),
    locker_id INTEGER REFERENCES locker(id),
    reservation_id INTEGER REFERENCES reservation(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action_type VARCHAR(64) NOT NULL,
    notes TEXT,
    due_date TIMESTAMP,
    returned_at TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT
);
```

### Indexes for Performance

```sql
CREATE INDEX idx_log_timestamp ON log(timestamp);
CREATE INDEX idx_log_action_type ON log(action_type);
CREATE INDEX idx_log_user_id ON log(user_id);
CREATE INDEX idx_log_ip_address ON log(ip_address);
```

## Action Types

### Authentication Events

- `login` - Successful user login
- `login_failed` - Failed login attempts (wrong password or user not found)
- `logout` - User logout
- `register` - Successful user registration
- `register_failed` - Failed registration attempts
- `auth_failed` - JWT token errors (invalid, missing, expired)

### Borrowing Events

- `borrow` - Item borrowed
- `return` - Item returned
- `overdue` - Item overdue

### Reservation Events

- `reservation_create` - New reservation created
- `reservation_cancel` - Reservation cancelled
- `reservation_modify` - Reservation modified
- `reservation_access` - Reservation accessed

### Administrative Events

- `admin_action` - General administrative actions
- `user_management` - User management operations
- `locker_management` - Locker management operations
- `system_maintenance` - System maintenance tasks

### Security Events

- `security_alert` - Security-related alerts
- `access_denied` - Access denied events

## Logged Information

Each log entry includes:

- **User Context**: User ID and name (when applicable)
- **Action Details**: Type of action performed
- **Descriptive Notes**: Human-readable description
- **IP Address**: Client IP address for security tracking
- **User Agent**: Browser/client information
- **Timestamp**: Exact time of the event
- **Related Entities**: Item, locker, or reservation IDs when relevant

## Implementation

### Logging Function

```python
def log_action(
    action_type,
    user_id=None,
    item_id=None,
    locker_id=None,
    details=None,
    ip_address=None,
    user_agent=None,
):
    """Log an action to the database with enhanced context"""
```

### Automatic Context Capture

The system automatically captures:

- IP address from `request.remote_addr`
- User agent from `request.headers.get('User-Agent')`
- User context from JWT tokens
- Timestamp of the event

## Usage Examples

### Authentication Logging

```python
# Successful login
log_action(
    "login",
    user.id,
    details=f"User '{username}' logged in successfully",
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent')
)

# Failed login
log_action(
    "login_failed",
    details=f"Failed login attempt for username '{username}' - User not found",
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent')
)
```

### Admin Action Logging

```python
# Locker creation
log_action(
    "admin_action",
    current_user_id,
    locker_id=locker.id,
    details=f"Admin created locker '{name}' (Number: {number})",
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent')
)
```

## Database Migration

### Automatic Migration

The system includes an automatic migration script (`db_migration.py`) that:

1. Updates the `action_type` column to VARCHAR(64) for longer action names
2. Adds `ip_address` and `user_agent` columns if they don't exist
3. Creates performance indexes for common queries
4. Runs automatically during system startup

### Manual Migration

To run migration manually:

```bash
cd backend
python db_migration.py
```

## Testing

### Test Script

Use the provided test script to verify logging functionality:

```bash
cd backend
python test_logging.py
```

This script tests:

- Failed login logging
- Successful login logging
- Logout logging
- Log retrieval and display

## Security Benefits

### Audit Trail

- Complete record of all user activities
- IP address tracking for security monitoring
- User agent information for client identification

### Threat Detection

- Failed authentication attempts
- Suspicious access patterns
- Unauthorized access attempts

### Compliance

- Detailed activity logs for regulatory requirements
- User accountability through comprehensive tracking
- Data retention and retrieval capabilities

## Performance Considerations

### Indexes

- Optimized queries on timestamp, action_type, user_id, and ip_address
- Efficient filtering and searching capabilities

### Data Retention

- Consider implementing log rotation for long-term deployments
- Archive old logs to maintain performance

## Monitoring and Alerts

### Key Metrics to Monitor

- Failed login attempts per user/IP
- Unusual access patterns
- Administrative actions
- System errors and exceptions

### Recommended Alerts

- Multiple failed login attempts from same IP
- Unusual admin actions
- System errors or exceptions
- High volume of failed authentication

## Author

**Alp Alpdogan**

In Memory of:

- Mehmet Ugurlu
- Yusuf Alpdogan

May their legacy inspire innovation and excellence.

---

_This logging system ensures comprehensive tracking of all Smart Locker System activities for security, compliance, and operational excellence._
