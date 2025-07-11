# Smart Locker System

A comprehensive locker management system designed for educational institutions, corporate environments, and public facilities. This enterprise-grade solution provides secure locker reservations, user management, and administrative oversight.

## Features

### Core Functionality

- **Locker Management**: Complete locker lifecycle management with status tracking
- **Reservation System**: Advanced booking system with conflict detection and time limits
- **User Management**: Multi-role user system with authentication and authorization
- **Item Tracking**: Equipment and item borrowing with return tracking
- **Administrative Dashboard**: Comprehensive management interface with reporting

### Technical Features

- **Modern Web Interface**: React-based frontend with responsive design
- **RESTful API**: Flask backend with comprehensive API endpoints
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **Security**: JWT authentication with role-based access control
- **Testing**: Comprehensive automated test suite with Puppeteer
- **Internationalization**: Multi-language support (English, French, Spanish, Turkish)

## System Requirements

### Prerequisites

- **Python 3.8+**: Core backend runtime
- **Node.js 16+**: Frontend development and build tools
- **PostgreSQL 12+**: Database server
- **Git**: Version control system

### Operating Systems

- **macOS**: 10.15+ (Catalina and later)
- **Linux**: Ubuntu 20.04+, CentOS 8+, or compatible distributions
- **Windows**: Windows 10+ (WSL2 recommended)

## Quick Start

### Automated Installation

The system includes a comprehensive deployment script that handles all setup automatically:

```bash
# Clone the repository
git clone https://github.com/your-org/smart-locker-system.git
cd smart-locker-system

# Run the deployment script
./start.sh --demo --reset-db --verbose
```

### Manual Installation

For custom deployments or development environments:

#### 1. Database Setup

```bash
# Install PostgreSQL
# macOS
brew install postgresql@14
brew services start postgresql@14

# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### 2. Backend Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://smart_locker_user:smartlockerpass123@localhost:5432/smart_locker_db"
export FLASK_ENV=development
export SECRET_KEY="your-secret-key-change-in-production"

# Initialize database
cd backend
python app.py --reset-db --demo
```

#### 3. Frontend Setup

```bash
# Install Node.js dependencies
cd frontend
npm install

# Start development server
npm run dev
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://smart_locker_user:smartlockerpass123@localhost:5432/smart_locker_db

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600

# Application Settings
MAX_RESERVATION_DURATION=7
DEFAULT_TIMEZONE=UTC
```

### Database Configuration

The system uses PostgreSQL with the following default settings:

- **Database**: `smart_locker_db`
- **User**: `smart_locker_user`
- **Password**: `smartlockerpass123`
- **Host**: `localhost`
- **Port**: `5432`

### Port Configuration

Default service ports:

- **Backend API**: `5172`
- **Frontend Development**: `5173`
- **Database**: `5432`

## Usage

### Deployment Script Options

The `start.sh` script supports various deployment modes:

```bash
# Development with demo data
./start.sh --demo --reset-db --verbose

# Minimal deployment (admin only)
./start.sh --minimal --test

# Production deployment
./start.sh --verbose

# Run with comprehensive testing
./start.sh --demo --test
```

### Command Line Options

| Option       | Description                        |
| ------------ | ---------------------------------- |
| `--demo`     | Load comprehensive demo data       |
| `--reset-db` | Reset and recreate database tables |
| `--verbose`  | Enable detailed logging            |
| `--minimal`  | Minimal mode (admin user only)     |
| `--test`     | Run comprehensive test suite       |
| `--help`     | Show usage information             |

### Default Credentials

#### Demo Mode

- **Admin**: `admin` / `admin123`
- **Student**: `student1` / `student123`
- **Manager**: `manager` / `manager123`
- **Supervisor**: `supervisor` / `supervisor123`

#### Minimal Mode

- **Admin**: `admin` / `admin123`

## Testing

### Automated Test Suite

The system includes a comprehensive test suite using Puppeteer for end-to-end testing. Puppeteer is automatically installed as part of the frontend setup.

```bash
# Run all tests
node tests/run_all_tests.js

# Run individual test modules
node tests/test_auth_flow.js
node tests/test_reservations.js
node tests/test_lockers.js
node tests/test_admin_dashboard.js
node tests/test_items.js
```

**Note**: Puppeteer is installed as a development dependency in the frontend. If you encounter issues, ensure it's properly installed:

```bash
cd frontend
npm install puppeteer
```

### API Testing

Test API endpoints using curl:

```bash
# Health check
curl http://localhost:5172/api/health

# Authentication
curl -X POST http://localhost:5172/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get lockers
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5172/api/lockers

# Create reservation
curl -X POST http://localhost:5172/api/reservations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"locker_id":1,"start_time":"2025-07-15T10:00:00Z","end_time":"2025-07-16T10:00:00Z"}'
```

### Test Coverage

The test suite covers:

- **Authentication Flow**: Login, logout, session management
- **Reservations**: Create, edit, cancel, conflict detection
- **Locker Management**: Status updates, filtering, search
- **Admin Dashboard**: User management, reports, settings
- **Items Module**: Borrowing, returning, inventory management

## API Documentation

### Authentication Endpoints

| Endpoint            | Method | Description         |
| ------------------- | ------ | ------------------- |
| `/api/auth/login`   | POST   | User authentication |
| `/api/auth/logout`  | POST   | User logout         |
| `/api/auth/refresh` | POST   | Token refresh       |

### Locker Endpoints

| Endpoint                   | Method | Description          |
| -------------------------- | ------ | -------------------- |
| `/api/lockers`             | GET    | List all lockers     |
| `/api/lockers/<id>`        | GET    | Get locker details   |
| `/api/lockers/<id>/status` | PUT    | Update locker status |

### Reservation Endpoints

| Endpoint                 | Method | Description             |
| ------------------------ | ------ | ----------------------- |
| `/api/reservations`      | GET    | List reservations       |
| `/api/reservations`      | POST   | Create reservation      |
| `/api/reservations/<id>` | GET    | Get reservation details |
| `/api/reservations/<id>` | PUT    | Update reservation      |
| `/api/reservations/<id>` | DELETE | Cancel reservation      |

### User Management

| Endpoint          | Method | Description              |
| ----------------- | ------ | ------------------------ |
| `/api/users`      | GET    | List users (admin only)  |
| `/api/users`      | POST   | Create user (admin only) |
| `/api/users/<id>` | GET    | Get user details         |
| `/api/users/<id>` | PUT    | Update user              |
| `/api/users/<id>` | DELETE | Delete user (admin only) |

## Development

### Project Structure

```
smart_locker_project/
├── backend/                 # Flask backend application
│   ├── app.py              # Main application file
│   ├── models.py           # Database models
│   ├── demo_data.py        # Demo data generation
│   ├── templates/          # HTML templates
│   ├── static/             # Static assets
│   └── utils/              # Utility modules
├── frontend/               # React frontend application
│   ├── src/                # Source code
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React contexts
│   │   └── utils/          # Utility functions
│   ├── public/             # Public assets
│   └── package.json        # Node.js dependencies
├── tests/                  # Test suite
│   ├── test_auth_flow.js   # Authentication tests
│   ├── test_reservations.js # Reservation tests
│   ├── test_lockers.js     # Locker tests
│   └── run_all_tests.js    # Test runner
├── docs/                   # Documentation
├── requirements.txt         # Python dependencies
├── start.sh               # Deployment script
└── README.md              # This file
```

### Development Workflow

1. **Setup Development Environment**

   ```bash
   ./start.sh --demo --reset-db --verbose
   ```

2. **Make Changes**

   - Backend: Edit files in `backend/`
   - Frontend: Edit files in `frontend/src/`

3. **Run Tests**

   ```bash
   node tests/run_all_tests.js
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

### Code Style

- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ESLint configuration
- **React**: Follow functional component patterns
- **CSS**: Use Tailwind CSS utility classes

## Deployment

### Production Deployment

For production environments:

1. **Environment Setup**

   ```bash
   # Set production environment variables
   export FLASK_ENV=production
   export DATABASE_URL="postgresql://user:pass@host:port/db"
   export SECRET_KEY="secure-production-secret"
   ```

2. **Database Migration**

   ```bash
   cd backend
   python app.py --reset-db
   ```

3. **Build Frontend**

   ```bash
   cd frontend
   npm run build
   ```

4. **Start Services**

   ```bash
   # Backend
   cd backend
   gunicorn -w 4 -b 0.0.0.0:5172 app:app

   # Frontend (serve built files)
   npx serve -s build -l 5173
   ```

### Docker Deployment

Docker configuration files are available for containerized deployment:

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individual containers
docker build -t smart-locker-backend ./backend
docker build -t smart-locker-frontend ./frontend
```

## Troubleshooting

### Common Issues

#### Backend Won't Start

```bash
# Check database connection
psql $DATABASE_URL

# Check Python environment
source .venv/bin/activate
python -c "import psycopg2; print('Database OK')"

# Check port availability
lsof -i :5172
```

#### Frontend Won't Start

```bash
# Check Node.js installation
node --version
npm --version

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### Database Connection Issues

```bash
# Start PostgreSQL service
# macOS
brew services start postgresql@14

# Linux
sudo systemctl start postgresql

# Check PostgreSQL status
pg_isready -h localhost -p 5432
```

### Log Files

- **Backend Logs**: Check console output or `backend/logs/`
- **Frontend Logs**: Check browser console or Vite output
- **Database Logs**: Check PostgreSQL logs

### Performance Optimization

- **Database**: Add indexes for frequently queried columns
- **Frontend**: Enable code splitting and lazy loading
- **Backend**: Use connection pooling for database connections
- **Caching**: Implement Redis for session storage

## Contributing

### Development Guidelines

1. **Fork the Repository**: Create your own fork
2. **Create Feature Branch**: `git checkout -b feature/your-feature`
3. **Make Changes**: Follow coding standards
4. **Add Tests**: Include tests for new functionality
5. **Submit Pull Request**: Provide clear description

### Code Review Process

1. **Automated Tests**: All tests must pass
2. **Code Quality**: Follow style guidelines
3. **Documentation**: Update relevant documentation
4. **Security**: Review for security implications

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

### Documentation

- [API Documentation](docs/API_DOCUMENTATION.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [Development Guide](docs/DEVELOPMENT_GUIDE.md)
- [Testing Guide](docs/TESTING_GUIDE.md)

### Contact

- **Issues**: [GitHub Issues](https://github.com/your-org/smart-locker-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/smart-locker-system/discussions)
- **Email**: support@smartlocker.com

## Changelog

### Version 2.0.0

- Comprehensive test suite with Puppeteer
- Professional deployment script
- Enhanced security features
- Improved documentation
- Enterprise-ready configuration

### Version 1.0.0

- Initial release
- Basic locker management
- User authentication
- Reservation system
