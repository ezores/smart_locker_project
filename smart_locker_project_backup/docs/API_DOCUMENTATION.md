# Smart Locker System - API Documentation

## Overview

The Smart Locker System provides a RESTful API for managing equipment borrowing and returning operations. The API is built with Flask and uses JWT authentication for secure access.

## Base URL

```
http://localhost:5050/api
```

## Authentication

All API endpoints require JWT authentication except for the login endpoint. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Authentication

#### POST /api/auth/login

Authenticate a user and receive a JWT token.

**Request Body:**

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

#### GET /api/user/profile

Get the current user's profile information.

**Response:**

```json
{
  "id": 1,
  "username": "admin",
  "role": "admin"
}
```

### Equipment Management

#### GET /api/items

Get all available items.

**Response:**

```json
[
  {
    "id": 1,
    "name": "Laptop Dell XPS 13",
    "locker_id": 1
  }
]
```

#### POST /api/borrow

Borrow an item.

**Request Body:**

```json
{
  "user_id": 1,
  "item_id": 1,
  "locker_id": 1
}
```

**Response:**

```json
{
  "message": "Item borrowed successfully"
}
```

#### POST /api/return

Return an item.

**Request Body:**

```json
{
  "user_id": 1,
  "item_id": 1,
  "locker_id": 1
}
```

**Response:**

```json
{
  "message": "Item returned successfully"
}
```

### Locker Management

#### GET /api/lockers

Get all lockers.

**Response:**

```json
[
  {
    "id": 1,
    "number": "A1",
    "location": "Location 1",
    "status": "available"
  }
]
```

### Administrative Endpoints

#### GET /api/admin/stats

Get system statistics (admin only).

**Response:**

```json
{
  "totalUsers": 10,
  "totalItems": 15,
  "totalLockers": 12,
  "activeBorrows": 5
}
```

#### GET /api/admin/users

Get all users (admin only).

**Response:**

```json
[
  {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
]
```

#### POST /api/admin/users

Create a new user (admin only).

**Request Body:**

```json
{
  "username": "newuser",
  "password": "password123",
  "role": "student"
}
```

#### PUT /api/admin/users/{user_id}

Update a user (admin only).

**Request Body:**

```json
{
  "username": "updateduser",
  "role": "student"
}
```

#### DELETE /api/admin/users/{user_id}

Delete a user (admin only).

#### GET /api/admin/logs

Get system activity logs (admin only).

**Response:**

```json
[
  {
    "id": 1,
    "action": "borrow",
    "user_id": 1,
    "item_id": 1,
    "locker_id": 1,
    "description": "",
    "timestamp": "2025-07-08T00:10:10.379250"
  }
]
```

#### GET /api/admin/reports

Generate reports (admin only).

**Query Parameters:**

- `type`: Report type (transactions)
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `range`: Date range (day, week, month, year)

**Response:**

```json
{
  "summary": {
    "total_transactions": 150,
    "borrows": 75,
    "returns": 75,
    "unique_users": 10,
    "unique_items": 15
  },
  "transactions": [
    {
      "id": 1,
      "user": "admin",
      "item": "Laptop Dell XPS 13",
      "action": "borrow",
      "timestamp": "2025-07-08T00:10:10.379250",
      "locker": "A1"
    }
  ]
}
```

#### GET /api/admin/export

Export reports (admin only).

**Query Parameters:**

- `type`: Report type (transactions)
- `format`: Export format (xlsx, pdf, csv)
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `range`: Date range (day, week, month, year)

**Response:** File download

## Error Responses

### 401 Unauthorized

```json
{
  "message": "No token provided"
}
```

### 404 Not Found

```json
{
  "message": "User not found"
}
```

### 500 Internal Server Error

```json
{
  "message": "Internal server error"
}
```

## Data Models

### User

```json
{
  "id": 1,
  "username": "admin",
  "role": "admin"
}
```

### Item

```json
{
  "id": 1,
  "name": "Laptop Dell XPS 13",
  "locker_id": 1
}
```

### Locker

```json
{
  "id": 1,
  "name": "A1",
  "status": "available"
}
```

### Log

```json
{
  "id": 1,
  "user_id": 1,
  "item_id": 1,
  "locker_id": 1,
  "action_type": "borrow",
  "timestamp": "2025-07-08T00:10:10.379250"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- 100 requests per minute per IP address
- 1000 requests per hour per user

## CORS

CORS is enabled for development. In production, configure allowed origins appropriately.

## Security

- JWT tokens expire after 24 hours
- Passwords are hashed using bcrypt
- All inputs are validated and sanitized
- SQL injection protection via SQLAlchemy ORM
- XSS protection via proper output encoding
