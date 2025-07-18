# Smart Locker Reservation System Documentation

## Overview

The Smart Locker Reservation System allows users to reserve lockers for specific time periods. This system provides a comprehensive booking mechanism with access control, time management, and administrative oversight.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Database Schema](#database-schema)
3. [API Endpoints](#api-endpoints)
4. [Frontend Implementation](#frontend-implementation)
5. [Access Control](#access-control)
6. [Integration Guide](#integration-guide)
7. [Error Handling](#error-handling)
8. [Security Considerations](#security-considerations)

## System Architecture

The reservation system follows a RESTful API architecture with the following components:

- **Backend**: Flask-based REST API with PostgreSQL database
- **Frontend**: React-based user interface
- **Authentication**: JWT-based authentication with role-based access control
- **Access Methods**: RFID card access and numeric access codes

## Database Schema

### Reservation Model

```python
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reservation_code = db.Column(db.String(16), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    locker_id = db.Column(db.Integer, db.ForeignKey("locker.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="active")  # active, cancelled, completed, expired
    access_code = db.Column(db.String(8), unique=True, nullable=False)  # 8-digit access code
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime)
    cancelled_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    modified_at = db.Column(db.DateTime)
    modified_by = db.Column(db.Integer, db.ForeignKey("user.id"))
```

### Key Fields Explanation

- **reservation_code**: Unique 8-character alphanumeric identifier
- **access_code**: 8-digit numeric code for locker access
- **status**: Current reservation state (active, cancelled, completed, expired)
- **start_time/end_time**: UTC timestamps for reservation period
- **user_id**: Foreign key to the user who made the reservation
- **locker_id**: Foreign key to the reserved locker

## API Endpoints

### 1. Get Reservations

**Endpoint**: `GET /api/reservations`

**Authentication**: Required (JWT)

**Query Parameters**:

- `status` (optional): Filter by reservation status
- `user_id` (optional): Filter by user ID (admin only)
- `locker_id` (optional): Filter by locker ID
- `start_date` (optional): Filter reservations starting after this date
- `end_date` (optional): Filter reservations ending before this date

**Response**:

```json
{
  "reservations": [
    {
      "id": 1,
      "reservation_code": "ABC12345",
      "user_id": 1,
      "locker_id": 1,
      "start_time": "2024-01-15T10:00:00",
      "end_time": "2024-01-15T12:00:00",
      "status": "active",
      "access_code": "12345678",
      "notes": "Equipment storage",
      "created_at": "2024-01-14T15:30:00",
      "user_name": "John Doe",
      "locker_name": "Locker A1",
      "locker_number": "001"
    }
  ]
}
```

### 2. Create Reservation

**Endpoint**: `POST /api/reservations`

**Authentication**: Required (JWT)

**Request Body**:

```json
{
  "locker_id": 1,
  "start_time": "2024-01-15T10:00:00",
  "end_time": "2024-01-15T12:00:00",
  "notes": "Equipment storage"
}
```

**Response**:

```json
{
  "message": "Reservation created successfully",
  "reservation": {
    "id": 1,
    "reservation_code": "ABC12345",
    "access_code": "12345678"
    // ... other reservation fields
  }
}
```

**Validation Rules**:

- Start time must be in the future
- End time must be after start time
- Locker must be available during the requested time period
- Maximum reservation duration: 24 hours
- Minimum reservation duration: 30 minutes

### 3. Get Single Reservation

**Endpoint**: `GET /api/reservations/{reservation_id}`

**Authentication**: Required (JWT)

**Access Control**: Users can only access their own reservations unless they are admin

### 4. Update Reservation

**Endpoint**: `PUT /api/reservations/{reservation_id}`

**Authentication**: Required (JWT)

**Request Body**:

```json
{
  "start_time": "2024-01-15T11:00:00",
  "end_time": "2024-01-15T13:00:00",
  "notes": "Updated notes"
}
```

**Restrictions**:

- Cannot modify reservations that have already started
- Cannot modify cancelled or completed reservations
- Time changes must not conflict with other reservations

### 5. Cancel Reservation

**Endpoint**: `POST /api/reservations/{reservation_id}/cancel`

**Authentication**: Required (JWT)

**Request Body**:

```json
{
  "reason": "No longer needed"
}
```

**Response**:

```json
{
  "message": "Reservation cancelled successfully",
  "reservation": {
    "id": 1,
    "status": "cancelled",
    "cancelled_at": "2024-01-14T16:00:00"
  }
}
```

### 6. Access Reservation (Numeric Code)

**Endpoint**: `POST /api/reservations/access/{access_code}`

**Authentication**: Required (JWT)

**Purpose**: Validate access code and open locker

**Response**:

```json
{
  "message": "Access granted",
  "reservation": {
    "id": 1,
    "locker_id": 1,
    "locker_name": "Locker A1"
  },
  "locker_opened": true
}
```

### 7. RFID Access

**Endpoint**: `POST /api/reservations/rfid-access/{rfid_tag}`

**Authentication**: Not required (RFID access is self-authenticating)

**Purpose**: Access reservation using RFID card

**Response**:

```json
{
  "message": "RFID access granted",
  "user": {
    "id": 1,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe"
  },
  "reservation": {
    "id": 1,
    "locker_id": 1,
    "access_code": "12345678"
  },
  "locker_opened": true
}
```

### 8. Export Reservations (Admin Only)

**Endpoint**: `GET /api/admin/export/reservations`

**Authentication**: Required (JWT + Admin role)

**Query Parameters**:

- `format`: Export format (csv, excel, pdf)
- `status` (optional): Filter by status

**Response**: File download with appropriate MIME type

## Frontend Implementation

### Key Components

#### 1. Reservations Page (`/reservations`)

**Features**:

- Calendar view for selecting dates
- List view of user's reservations
- Create new reservation modal
- Edit existing reservations
- Cancel reservations
- Export functionality (admin only)

#### 2. Reservation Form

**Fields**:

- Locker selection dropdown
- Start date/time picker
- End date/time picker
- Notes textarea

**Validation**:

- Real-time availability checking
- Time conflict detection
- Duration limits enforcement

#### 3. Access Code Display

**Security Features**:

- Access codes are only shown to reservation owner
- Codes are masked by default with show/hide toggle
- Automatic code regeneration on security breach

### State Management

```javascript
const [reservations, setReservations] = useState([]);
const [lockers, setLockers] = useState([]);
const [loading, setLoading] = useState(true);
const [selectedDate, setSelectedDate] = useState(new Date());
const [showCreateModal, setShowCreateModal] = useState(false);
const [formData, setFormData] = useState({
  locker_id: "",
  start_time: "",
  end_time: "",
  notes: "",
});
```

### API Integration

```javascript
// Fetch reservations
const fetchReservations = async () => {
  try {
    const params = new URLSearchParams();
    if (filterStatus) params.append("status", filterStatus);

    const response = await api.get(`/reservations?${params}`);
    setReservations(response.data.reservations);
  } catch (error) {
    console.error("Error fetching reservations:", error);
  }
};

// Create reservation
const createReservation = async (reservationData) => {
  try {
    const response = await api.post("/reservations", reservationData);
    return response.data;
  } catch (error) {
    throw error;
  }
};
```

## Access Control

### Authentication Methods

1. **JWT Token Authentication**: Required for all API endpoints except RFID access
2. **RFID Card Access**: Direct hardware access without JWT requirement
3. **Numeric Access Code**: 8-digit code for manual locker access

### Authorization Levels

1. **Student Users**:

   - Can create, view, and cancel their own reservations
   - Cannot access other users' reservations
   - Cannot export data

2. **Admin Users**:
   - Full access to all reservations
   - Can modify any reservation
   - Can export reservation data
   - Can access system statistics

### Security Features

- **Access Code Generation**: Cryptographically secure random 8-digit codes
- **Reservation Code Generation**: Unique 8-character alphanumeric identifiers
- **Time-based Access Control**: Reservations are only accessible during their time window
- **RFID Integration**: Secure hardware-based access control

## Integration Guide

### For New Developers

#### 1. Setting Up Development Environment

```bash
# Backend setup
cd backend
pip install -r requirements.txt
python app.py

# Frontend setup
cd frontend
npm install
npm start
```

#### 2. Database Migration

```python
# Run database initialization
from app import db, init_db_func
init_db_func()
```

#### 3. Creating Your First Reservation

```javascript
// Example API call
const reservationData = {
  locker_id: 1,
  start_time: "2024-01-15T10:00:00",
  end_time: "2024-01-15T12:00:00",
  notes: "Test reservation",
};

const response = await api.post("/reservations", reservationData);
console.log("Reservation created:", response.data);
```

#### 4. Integrating with External Systems

**Webhook Integration**:

```python
# Add webhook support for reservation events
@app.route('/api/webhooks/reservation-created', methods=['POST'])
def reservation_created_webhook():
    # Handle external system integration
    pass
```

**Calendar Integration**:

```javascript
// Export to calendar formats
const exportToCalendar = (reservation) => {
  const icsContent = generateICS(reservation);
  downloadFile(icsContent, "reservation.ics");
};
```

### Custom Implementation Examples

#### 1. Adding Custom Validation

```python
def validate_reservation_time(start_time, end_time):
    """Custom validation for reservation times"""
    duration = end_time - start_time

    # Custom business rules
    if duration.total_seconds() < 1800:  # 30 minutes minimum
        raise ValueError("Minimum reservation duration is 30 minutes")

    if duration.total_seconds() > 86400:  # 24 hours maximum
        raise ValueError("Maximum reservation duration is 24 hours")

    # Check business hours
    if start_time.hour < 8 or end_time.hour > 22:
        raise ValueError("Reservations only allowed between 8 AM and 10 PM")
```

#### 2. Custom Notification System

```python
def send_reservation_notification(reservation, event_type):
    """Send notifications for reservation events"""
    user = reservation.user

    notifications = {
        'created': f"Reservation {reservation.reservation_code} created",
        'cancelled': f"Reservation {reservation.reservation_code} cancelled",
        'expiring': f"Reservation {reservation.reservation_code} expires in 1 hour"
    }

    # Send email, SMS, or push notification
    send_notification(user.email, notifications[event_type])
```

## Error Handling

### Common Error Scenarios

1. **Locker Unavailable**:

   ```json
   {
     "error": "Locker not available",
     "details": "Locker is already reserved for the requested time period",
     "available_times": ["2024-01-15T14:00:00", "2024-01-15T16:00:00"]
   }
   ```

2. **Invalid Time Range**:

   ```json
   {
     "error": "Invalid time range",
     "details": "End time must be after start time"
   }
   ```

3. **Access Denied**:
   ```json
   {
     "error": "Access denied",
     "details": "You can only access your own reservations"
   }
   ```

### Frontend Error Handling

```javascript
const handleReservationError = (error) => {
  if (error.response?.status === 409) {
    setError("Locker is not available for the selected time");
  } else if (error.response?.status === 400) {
    setError("Invalid reservation data");
  } else {
    setError("An unexpected error occurred");
  }
};
```

## Security Considerations

### Data Protection

1. **Access Code Security**:

   - Access codes are generated using cryptographically secure random numbers
   - Codes are unique across the entire system
   - Codes expire when reservations end

2. **User Data Privacy**:

   - Users can only access their own reservation data
   - Admin access is logged and audited
   - Sensitive data is not exposed in API responses

3. **Time-based Security**:
   - Reservations are only accessible during their active time window
   - Expired reservations cannot be accessed
   - System automatically updates reservation status

### Best Practices

1. **Input Validation**:

   - All user inputs are validated on both client and server side
   - SQL injection prevention through parameterized queries
   - XSS prevention through proper data sanitization

2. **Rate Limiting**:

   - API endpoints have rate limiting to prevent abuse
   - Reservation creation is limited per user per day

3. **Audit Logging**:
   - All reservation activities are logged
   - Access attempts are tracked
   - Failed authentication attempts are monitored

## Testing

### Unit Tests

```python
def test_create_reservation():
    """Test reservation creation"""
    reservation_data = {
        'locker_id': 1,
        'start_time': datetime.utcnow() + timedelta(hours=1),
        'end_time': datetime.utcnow() + timedelta(hours=3),
        'notes': 'Test reservation'
    }

    response = client.post('/api/reservations',
                          json=reservation_data,
                          headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 201
    assert 'reservation_code' in response.json['reservation']
```

### Integration Tests

```javascript
describe("Reservation System", () => {
  test("should create and access reservation", async () => {
    // Create reservation
    const reservation = await createReservation(testData);
    expect(reservation.access_code).toBeDefined();

    // Access with code
    const access = await accessReservation(reservation.access_code);
    expect(access.locker_opened).toBe(true);
  });
});
```

## Performance Considerations

### Database Optimization

1. **Indexing**:

   ```sql
   CREATE INDEX idx_reservations_time ON reservations(start_time, end_time);
   CREATE INDEX idx_reservations_status ON reservations(status);
   CREATE INDEX idx_reservations_user ON reservations(user_id);
   ```

2. **Query Optimization**:
   - Use pagination for large result sets
   - Implement caching for frequently accessed data
   - Optimize JOIN queries with proper indexing

### Frontend Performance

1. **Data Fetching**:

   - Implement lazy loading for reservation lists
   - Use React Query for caching and synchronization
   - Debounce search inputs

2. **Component Optimization**:
   - Use React.memo for expensive components
   - Implement virtual scrolling for large lists
   - Optimize re-renders with proper dependency arrays

## Monitoring and Analytics

### Key Metrics

1. **Usage Statistics**:

   - Total reservations per day/week/month
   - Average reservation duration
   - Most popular time slots
   - Locker utilization rates

2. **Performance Metrics**:

   - API response times
   - Database query performance
   - Error rates and types

3. **User Behavior**:
   - Reservation cancellation rates
   - No-show rates
   - Peak usage times

### Monitoring Implementation

```python
@app.route('/api/admin/stats/reservations')
@jwt_required()
@admin_required
def get_reservation_stats():
    """Get reservation system statistics"""
    stats = {
        'total_reservations': Reservation.query.count(),
        'active_reservations': Reservation.query.filter_by(status='active').count(),
        'utilization_rate': calculate_utilization_rate(),
        'popular_times': get_popular_time_slots()
    }
    return jsonify(stats)
```

## Future Enhancements

### Planned Features

1. **Recurring Reservations**: Support for weekly/monthly recurring bookings
2. **Waitlist System**: Queue system for popular time slots
3. **Mobile App**: Native mobile application with push notifications
4. **IoT Integration**: Enhanced sensor integration for automatic status updates
5. **AI Optimization**: Machine learning for optimal locker allocation

### API Versioning

Future API versions will maintain backward compatibility:

```
/api/v1/reservations  # Current version
/api/v2/reservations  # Future version with enhanced features
```

## Support and Troubleshooting

### Common Issues

1. **Reservation Not Found**: Check reservation code and user permissions
2. **Access Code Not Working**: Verify reservation is active and within time window
3. **Locker Won't Open**: Check hardware connection and RS485 communication

### Debug Mode

Enable debug logging for troubleshooting:

```python
# In app.py
app.config['DEBUG'] = True
logging.getLogger().setLevel(logging.DEBUG)
```

### Contact Information

For technical support or integration questions:

- Email: support@smartlocker.com
- Documentation: https://docs.smartlocker.com
- GitHub Issues: https://github.com/smartlocker/issues

---

_This documentation is maintained by the Smart Locker development team. Last updated: January 2024_
