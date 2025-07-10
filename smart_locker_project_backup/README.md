# Smart Locker System

A modern, full-stack smart locker management system built with Flask (Python) backend and React (JavaScript) frontend. The system provides secure equipment borrowing and returning functionality with comprehensive user management, logging, and reporting capabilities.

## 🌟 Features

### Core Functionality

- **RFID Card Authentication** - Secure access using RFID cards
- **User ID Authentication** - Alternative login using numeric user IDs
- **Equipment Management** - Track and manage equipment inventory
- **Locker Management** - Monitor locker status and locations
- **Borrow/Return System** - Streamlined equipment checkout process
- **Real-time Logging** - Comprehensive activity tracking

### User Management

- **Multi-role Support** - Admin and Student roles
- **User Authentication** - Secure login with JWT tokens
- **Profile Management** - User account administration
- **Permission Control** - Role-based access control

### Administrative Features

- **Dashboard Analytics** - Real-time system statistics
- **Reporting System** - Export reports in Excel, PDF, and CSV formats
- **Activity Logs** - Detailed system activity monitoring
- **Data Management** - CRUD operations for users, items, and lockers

### User Experience

- **Multi-language Support** - English, French, Spanish, Turkish
- **Dark Mode** - Modern dark/light theme toggle
- **Responsive Design** - Works on desktop and mobile devices
- **Modern UI/UX** - Clean, intuitive interface

## 🏗️ Project Structure

```
smart_locker_project/
├── 📁 backend/                    # Flask backend application
│   ├── 📁 api/                   # API endpoints
│   ├── 📁 models/                # Database models
│   ├── 📁 utils/                 # Utility functions
│   ├── 📁 config/                # Configuration files
│   └── 📁 tests/                 # Backend tests
├── 📁 frontend/                  # React frontend application
│   ├── 📁 src/
│   │   ├── 📁 components/        # Reusable UI components
│   │   ├── 📁 pages/            # Page components
│   │   ├── 📁 contexts/         # React contexts
│   │   ├── 📁 hooks/            # Custom React hooks
│   │   └── 📁 utils/            # Frontend utilities
│   └── 📁 public/               # Static assets
├── 📁 docs/                     # Documentation
├── 📁 scripts/                  # Development scripts
└── 📁 data/                     # Database and data files
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- PostgreSQL (for production)

### 1. Setup PostgreSQL

First, install and configure PostgreSQL:

```bash
./setup_postgresql.sh
```

This script will:

- Install PostgreSQL (macOS: Homebrew, Linux: apt)
- Start the PostgreSQL service
- Create the database and configure users
- Test the connection

### 2. Start the System

#### Development Mode with Demo Data

```bash
./start.sh --dev --demo --verbose
```

#### Production Mode

```bash
./start.sh --prod
```

#### Testing Mode with Simple Demo

```bash
./start.sh --test --simple-demo
```

#### Reset Database and Load Demo Data

```bash
./start.sh --dev --reset-db --verbose
```

## Startup Script Options

### Environment Options

- `--dev`: Development mode (default)
- `--prod`: Production mode
- `--test`: Testing mode

### Demo Options

- `--demo`: Load comprehensive demo data (10 users, 8 lockers, 25 items, 100 logs)
- `--simple-demo`: Load minimal demo data (2 users, 2 lockers, 2 items)
- `--reset-db`: Reset database and load demo data

### Configuration Options

- `--verbose`: Enable verbose output
- `--port PORT`: Backend port (default: 5172)
- `--frontend-port PORT`: Frontend port (default: 5173)

### Database Options

- `--db-host HOST`: Database host (default: localhost)
- `--db-port PORT`: Database port (default: 5432)
- `--db-name NAME`: Database name (default: smart_locker)
- `--db-user USER`: Database user (default: postgres)
- `--db-password PASS`: Database password (default: postgres)

## 🔧 Configuration

### Environment Variables

The system uses the following environment variables for database configuration:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=smart_locker
export DB_USER=postgres
export DB_PASSWORD=postgres
```

### Database Setup

The system uses PostgreSQL for better scalability, performance, and enterprise features. The database includes enhanced models with additional fields.

## Database Schema

### Enhanced Models

The system now includes enhanced database models with additional fields:

#### Users

- `id`, `username`, `password_hash`, `rfid_tag`, `qr_code`, `role`
- `email`, `first_name`, `last_name`, `student_id`, `created_at`, `is_active`

#### Lockers

- `id`, `name`, `location`, `capacity`, `status` (active/maintenance/inactive)

#### Items

- `id`, `name`, `description`, `category`, `condition`, `serial_number`
- `purchase_date`, `warranty_expiry`, `locker_id`, `is_available`, `created_at`

#### Logs

- `id`, `user_id`, `item_id`, `locker_id`, `timestamp`, `action_type`
- `notes`, `due_date`, `returned_at`

#### Borrows (New)

- `id`, `user_id`, `item_id`, `borrowed_at`, `due_date`, `returned_at`
- `status` (borrowed/returned/overdue), `notes`

## Demo Data

### Comprehensive Demo Data

When using `--demo`, the system creates:

- **10 Users**: 2 admins, 8 students
- **8 Lockers**: Different locations and capacities
- **25 Items**: Electronics, books, tools, audio/video equipment
- **100 Log Entries**: Various actions with timestamps
- **Active Borrows**: 30% of items are currently borrowed

### Simple Demo Data

When using `--simple-demo`, the system creates:

- **2 Users**: 1 admin, 1 student
- **2 Lockers**: Basic configuration
- **2 Items**: Laptop and tablet

## Demo Credentials

### Admin Users

- Username: `admin`, Password: `admin123`
- Username: `manager`, Password: `manager123`

### Student Users

- Username: `student1` through `student10`, Password: `student123`

## 👥 User Roles

### Admin

- Full system access
- User management
- Equipment management
- Locker management
- System reports and analytics
- Activity monitoring

### Student

- Borrow equipment
- Return equipment
- View personal history
- Access to assigned lockers

## 🔐 Authentication Methods

### RFID Card Authentication

- Primary authentication method
- Secure card-based access
- Real-time validation

### User ID Authentication

- Alternative authentication method
- Numeric user ID input
- Fallback when RFID cards are unavailable

## 📊 API Documentation

### Health Check

- `GET /api/health`: System health status and database connection

### Authentication Endpoints

- `POST /api/auth/login` - User login
- `GET /api/user/profile` - Get user profile

### Equipment Management

- `GET /api/items` - List all items
- `GET /api/lockers` - List all lockers
- `POST /api/borrow` - Borrow equipment
- `POST /api/return` - Return equipment

### Administrative Endpoints

- `GET /api/admin/stats` - System statistics
- `GET /api/admin/recent-activity` - Recent activity
- `GET /api/admin/active-borrows` - Currently borrowed items
- `GET /api/admin/reports` - Generate reports
- `GET /api/admin/export` - Export data in various formats
- `GET /api/admin/users` - User management
- `GET /api/admin/logs` - Activity logs

## 🧪 Testing

### Backend Tests

```bash
# Run backend tests
python -m pytest tests/
```

### Frontend Tests

```bash
# Run frontend tests
npm test
```

## 📝 Development

### Code Style

- Backend: Follow PEP 8 Python style guide
- Frontend: Use ESLint and Prettier
- Components: Use functional components with hooks

## 🔧 Troubleshooting

### PostgreSQL Connection Issues

1. Ensure PostgreSQL is running:

   ```bash
   # macOS
   brew services list | grep postgresql

   # Linux
   sudo systemctl status postgresql
   ```

2. Check database connection:

   ```bash
   PGPASSWORD=postgres psql -h localhost -U postgres -d smart_locker
   ```

3. Reset database if needed:
   ```bash
   ./start.sh --dev --reset-db --verbose
   ```

### Port Conflicts

If ports are already in use, specify different ports:

```bash
./start.sh --dev --demo --port 5173 --frontend-port 5174
```

### Verbose Debugging

Enable verbose mode for detailed logging:

```bash
./start.sh --dev --demo --verbose
```

## 🚀 Production Deployment

For production deployment:

1. Use a dedicated PostgreSQL server
2. Set secure database credentials
3. Configure environment variables
4. Use production mode:

   ```bash
   ./start.sh --prod --db-host your-db-server --db-user your-user --db-password your-password
   ```

5. Consider using a process manager like PM2 or systemd
6. Set up proper logging and monitoring
7. Configure SSL/TLS for secure connections

## 📚 Migration Notes

### Removed SQLite Files

- `smart_locker_project/backend/db/locker.db`
- `instance/smart_locker.db-journal`

### New Dependencies

- `psycopg2-binary==2.9.9`: PostgreSQL adapter
- `SQLAlchemy==2.0.23`: Enhanced ORM features

### Backward Compatibility

The system maintains all existing functionality while adding:

- Enhanced data models
- Better scalability
- Improved performance
- Enterprise-grade database features
