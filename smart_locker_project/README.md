# Smart Locker System

A comprehensive locker management system with Flask backend and React frontend, featuring JWT authentication, PostgreSQL support, role-based access control, and comprehensive logging.

## Features Overview

### 🔐 Authentication & Security

- **JWT (JSON Web Token) Authentication**: Secure token-based authentication with configurable expiration
- **Role-Based Access Control**: Admin and student roles with different permissions
- **Password Hashing**: Secure password storage using Werkzeug's password hashing
- **CORS Support**: Cross-origin resource sharing enabled for frontend integration

### 🗄️ Database & Storage

- **PostgreSQL Support**: Production-ready database with connection pooling
- **SQLite Fallback**: Development-friendly local database
- **Database Migrations**: Automatic schema creation and updates
- **Connection Pooling**: Optimized database connections for high concurrency

### 👥 User Management

- **User Registration**: Self-service user registration with validation
- **Profile Management**: User profiles with department and balance tracking
- **RFID/QR Support**: Ready for hardware integration with RFID tags and QR codes
- **User Status Tracking**: Active/inactive user management

### 🏢 Locker Management

- **Locker Assignment**: Automatic locker assignment based on availability
- **Capacity Management**: Track locker occupancy and capacity limits
- **Status Tracking**: Available, occupied, maintenance status tracking
- **Location Management**: Room and location-based locker organization

### 📦 Item Management

- **Item Catalog**: Comprehensive item database with categories
- **Condition Tracking**: Item condition monitoring (good, fair, poor)
- **Status Management**: Available, borrowed, maintenance status
- **Category Organization**: Electronics, books, tools, sports equipment

### 🔄 Borrow/Return System

- **Borrowing Process**: Complete item borrowing workflow
- **Due Date Management**: Configurable due dates with notifications
- **Return Processing**: Item return with condition assessment
- **Status Tracking**: Active, returned, overdue status management

### 🔌 Hardware Integration

- **RS485 Locker Control**: Direct hardware control for opening/closing lockers
- **Mock Mode Support**: Development-friendly simulation without hardware
- **Real-time Status**: Get locker status via RS485 communication
- **Connection Testing**: Built-in RS485 connection diagnostics
- **Command Logging**: All hardware commands logged for audit trail

### �� Admin & Reporting

- **System Statistics**: Real-time dashboard with key metrics
- **Activity Logging**: Comprehensive audit trail of all actions
- **Export Functionality**: CSV, Excel, and PDF export for all data
- **Admin Dashboard**: Web-based admin interface
- **Multi-format Reports**: Comprehensive system reports in multiple formats

### �� Frontend Features

- **React Application**: Modern, responsive web interface
- **Real-time Updates**: Live data updates without page refresh
- **Responsive Design**: Mobile-friendly interface
- **Dark Mode Support**: User preference for dark/light themes
- **Internationalization**: Multi-language support (EN, ES, FR, TR)

### 📝 Logging & Monitoring

- **Comprehensive Logging**: All actions logged with timestamps
- **IP Tracking**: User IP address logging for security
- **User Agent Logging**: Browser/client information tracking
- **Error Handling**: Detailed error logging and reporting

## Architecture

### Backend (Flask)

```
backend/
├── app.py              # Main application with all endpoints
├── requirements.txt    # Python dependencies
└── logs/              # Application logs
```

### Frontend (React)

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Page components
│   ├── contexts/      # React contexts (Auth, Language)
│   └── main.jsx       # Application entry point
├── package.json       # Node.js dependencies
└── vite.config.js     # Vite configuration
```

### Database Schema

- **Users**: User accounts with roles and profiles
- **Lockers**: Physical locker locations and status
- **Items**: Inventory items with categories and conditions
- **Borrows**: Active borrowing transactions
- **Returns**: Completed return transactions
- **Logs**: System activity audit trail

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL (optional, SQLite for development)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd smart_locker_project
   ```

2. **Set up Python environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up Node.js environment**

   ```bash
   cd frontend
   npm install
   ```

4. **Configure database (optional)**

   ```bash
   # For PostgreSQL (production)
   export DATABASE_URL="postgresql://user:password@localhost/smart_locker"

   # For SQLite (development - default)
   # No configuration needed
   ```

### Running the System

#### Development Mode (Minimal Data)

```bash
./start_dev.sh
```

- Backend: http://localhost:5051
- Frontend: http://localhost:3000
- Minimal demo data for quick testing

#### Production Mode (Full Demo Data)

```bash
./start_services.sh
```

- Full demo data with users, lockers, and items
- Complete system for demonstration

#### Manual Start

```bash
# Backend only
cd backend
source ../.venv/bin/activate
python app.py --init-db --port 5051

# Frontend only
cd frontend
npm run dev
```

### Default Credentials

- **Admin**: `admin` / `admin123`
- **Student**: `student` / `password123`

## API Endpoints

### Authentication

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Users

- `GET /api/users` - List users (admin only)
- `GET /api/users/<id>` - Get user details

### Lockers

- `GET /api/lockers` - List lockers
- `GET /api/lockers?status=available` - Filter by status

### Items

- `GET /api/items` - List items
- `GET /api/items?category=Electronics` - Filter by category

### Borrows

- `GET /api/borrows` - List borrows
- `POST /api/borrows` - Create borrow
- `POST /api/borrows/<id>/return` - Return item

### Admin

- `GET /api/admin/stats` - System statistics
- `GET /api/logs` - Activity logs
- `GET /api/admin/export/logs` - Export logs as CSV

### RS485 Hardware Control

- `POST /api/lockers/<id>/open` - Open locker via RS485
- `POST /api/lockers/<id>/close` - Close locker via RS485
- `GET /api/lockers/<id>/status` - Get locker status via RS485
- `GET /api/admin/rs485/test` - Test RS485 connection

### Export Functionality

- `GET /api/admin/export/users?format=csv|excel|pdf` - Export users data
- `GET /api/admin/export/borrows?format=csv|excel|pdf` - Export borrows data
- `GET /api/admin/export/system?format=csv|excel|pdf&type=comprehensive` - Export system report

## Testing

### Comprehensive Test Suite

```bash
./test_system.sh
```

The test suite includes:

- **Backend Health Checks**: API availability and response times
- **Authentication Tests**: Login, token validation, role-based access
- **CRUD Operations**: Create, read, update, delete operations
- **Authorization Tests**: Admin vs student access controls
- **Database Integrity**: Schema validation and data consistency
- **Performance Tests**: Response time and load testing
- **Error Handling**: Invalid inputs and edge cases
- **Logging Tests**: Audit trail verification
- **Frontend Tests**: React application health checks

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: API endpoint testing
3. **Authorization Tests**: Role-based access control
4. **Performance Tests**: Response time and load testing
5. **Error Handling**: Invalid inputs and edge cases
6. **Database Tests**: Schema and data integrity
7. **Logging Tests**: Audit trail verification

## Configuration

### Environment Variables

```bash
# Database configuration
DATABASE_URL=postgresql://user:password@localhost/smart_locker

# JWT configuration
JWT_SECRET_KEY=your-secret-key-here

# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=true
```

### Database Configuration

- **SQLite**: Default for development, no configuration needed
- **PostgreSQL**: Set `DATABASE_URL` environment variable
- **Connection Pooling**: Automatic for PostgreSQL, optimized for SQLite

### Logging Configuration

- **File Logging**: `logs/app.log`
- **Console Logging**: Real-time console output
- **Log Levels**: INFO, WARNING, ERROR, DEBUG
- **Log Format**: Timestamp, level, message, context

## Deployment

### Production Setup

1. **Database**: Use PostgreSQL for production
2. **Environment**: Set production environment variables
3. **Logging**: Configure log rotation and monitoring
4. **Security**: Use strong JWT secrets and HTTPS
5. **Monitoring**: Set up application monitoring

### Docker Deployment (Optional)

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["python", "app.py", "--port", "5051"]
```

## Troubleshooting

### Common Issues

#### Database Locked (SQLite)

```bash
# Kill existing processes
pkill -f "python.*app.py"
# Remove database file
rm -f backend/smart_locker.db
# Restart with fresh database
python app.py --init-db
```

#### Port Already in Use

```bash
# Find process using port
lsof -i :5051
# Kill process
kill -9 <PID>
```

#### Frontend Build Issues

```bash
# Clear node modules
rm -rf frontend/node_modules
npm install
```

#### JWT Token Issues

```bash
# Check token expiration
# Verify JWT_SECRET_KEY is set
# Restart backend to refresh tokens
```

### Debug Mode

```bash
# Backend with debug logging
python app.py --port 5051 --debug

# Frontend with debug mode
npm run dev -- --debug
```

## Script Usage

### Overview

| Script              | Purpose                                                                                                                 | Usage Example                                | Stops With        |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | ----------------- |
| `start_dev.sh`      | Development: starts backend & frontend, hot reload, auto-heals Python issues, loads demo data, checks all dependencies. | `./start_dev.sh --demo --verbose --reset-db` | Ctrl+C            |
| `start_services.sh` | Production: starts backend only, optimized for deployment, suppresses non-essential npm output, no hot reload.          | `./start_services.sh --demo --reset-db`      | Ctrl+C or systemd |

**Key Differences:**

- `start_dev.sh` is for local development and testing. It runs both backend and frontend, supports hot reload, and is robust against common Python/Node issues.
- `start_services.sh` is for production or deployment (e.g., Raspberry Pi). It runs only the backend, is optimized for performance, and is designed to be used with systemd or similar service managers.

**Stopping Services:**

- In development, simply press `Ctrl+C` in the terminal to stop both backend and frontend.
- In production, use `systemctl stop smart-locker-backend` if running as a service, or `Ctrl+C` if running manually.

**No need for separate stop scripts.**

## Development

### Adding New Features

1. **Backend**: Add endpoints to `app.py`
2. **Frontend**: Create components in `frontend/src/`
3. **Database**: Update models in `app.py`
4. **Testing**: Add tests to `test_system.sh`

### Code Structure

- **Single app.py**: All backend functionality in one file
- **Minimal Mode**: Quick testing with `--minimal` flag
- **Full Mode**: Complete system with demo data
- **Modular Frontend**: React components and contexts

### Testing Strategy

- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **End-to-End Tests**: Complete workflow testing
- **Performance Tests**: Load and stress testing

## Security Features

### Authentication

- JWT tokens with configurable expiration
- Secure password hashing with Werkzeug
- Role-based access control (admin/student)
- Token refresh and validation

### Authorization

- Admin-only endpoints for sensitive operations
- User-specific data access controls
- Audit logging for all actions
- IP address and user agent tracking

### Data Protection

- Input validation and sanitization
- SQL injection prevention with SQLAlchemy
- CORS configuration for frontend security
- Secure session management

## Performance Optimization

### Database

- Connection pooling for PostgreSQL
- Indexed queries for fast lookups
- Pagination for large datasets
- Efficient relationship loading

### API

- Response caching where appropriate
- Optimized database queries
- Minimal data transfer
- Error handling and logging

### Frontend

- React optimization with hooks
- Lazy loading for components
- Efficient state management
- Responsive design for mobile

## Monitoring and Logging

### Application Logs

- All API requests logged
- Error tracking and reporting
- Performance metrics
- User activity audit trail

### System Health

- Database connection monitoring
- API response time tracking
- Error rate monitoring
- Resource usage tracking

## Future Enhancements

### Planned Features

- **Hardware Integration**: RFID reader and locker control
- **Mobile App**: React Native mobile application
- **Real-time Notifications**: WebSocket-based alerts
- **Advanced Reporting**: Analytics and insights
- **Multi-tenant Support**: Multiple organization support

### Technical Improvements

- **Microservices**: Service-oriented architecture
- **Containerization**: Docker and Kubernetes support
- **CI/CD Pipeline**: Automated testing and deployment
- **Monitoring**: Prometheus and Grafana integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Check the troubleshooting section
- Review the test logs in `test_logs/`
- Check application logs in `logs/app.log`
- Open an issue with detailed error information
