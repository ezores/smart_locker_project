# Smart Locker System

A comprehensive smart locker management system with RFID access, reservation system, and admin dashboard.

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- npm

### Installation & Startup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd smart_locker_project
   ```

2. **Start the system with demo data**

   ```bash
   ./start.sh --demo --verbose --reset-db
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5172
   - Health Check: http://localhost:5172/api/health

### Demo Credentials

When running with `--demo` flag, the following users are available:

**Admin Users:**

- Username: `admin` | Password: `admin123`
- Username: `manager` | Password: `manager123`
- Username: `supervisor` | Password: `supervisor123`

**Student Users:**

- Username: `student1` through `student50` | Password: `student123`

### Startup Options

```bash
# Full demo with comprehensive data
./start.sh --demo --verbose --reset-db

# Minimal mode (admin user only, empty lockers)
./start.sh --minimal --verbose --reset-db

# Run with tests
./start.sh --demo --test --verbose --reset-db

# Production mode (no demo data)
./start.sh --verbose
```

### API Testing

Test the API endpoints:

```bash
# Health check
curl http://localhost:5172/api/health

# Login
curl -X POST http://localhost:5172/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get lockers (with token from login)
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:5172/api/lockers
```

## Features

- **RFID Access Control**: Secure locker access via RFID tags
- **Reservation System**: Book lockers in advance with access codes
- **Admin Dashboard**: Comprehensive management interface
- **Multi-language Support**: English, French, Spanish, Turkish
- **Reporting**: Export data in CSV, Excel, and PDF formats
- **Real-time Monitoring**: Live status updates and notifications
- **Payment Integration**: Stripe payment processing
- **Audit Logging**: Complete activity tracking

## Architecture

- **Backend**: Flask (Python) with PostgreSQL
- **Frontend**: React with Vite
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens
- **Real-time**: WebSocket support
- **Hardware**: RS485 protocol for locker control

## Development

### Project Structure

```
smart_locker_project/
├── backend/          # Flask API server
├── frontend/         # React application
├── docs/            # Documentation
├── tests/           # Test suites
└── scripts/         # Utility scripts
```

### Environment Variables

The system uses environment variables for configuration:

- `DATABASE_URL`: PostgreSQL connection string
- `ADMIN_PASSWORD`: Admin user password (default: admin123)
- `MANAGER_PASSWORD`: Manager password (default: manager123)
- `SUPERVISOR_PASSWORD`: Supervisor password (default: supervisor123)
- `STUDENT_PASSWORD`: Student password (default: student123)

## Troubleshooting

### Common Issues

1. **Port already in use**: The script will automatically kill conflicting processes
2. **Database connection issues**: Ensure PostgreSQL is running and accessible
3. **npm installation fails**: The script includes retry logic and cache cleaning
4. **Frontend not loading**: Check if Vite dev server is running on port 5173

### Manual Cleanup

If the startup script fails, manually clean up:

```bash
# Kill processes on ports
lsof -ti:5172 | xargs kill -9
lsof -ti:5173 | xargs kill -9

# Clean npm cache
cd frontend && npm cache clean --force

# Restart PostgreSQL
brew services restart postgresql@14  # macOS
sudo systemctl restart postgresql    # Linux
```

## License

MIT License - see LICENSE file for details.
