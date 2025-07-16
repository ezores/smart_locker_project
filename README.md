# Smart Locker System

A comprehensive smart locker management system with RFID access, reservation system, and admin dashboard.

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+ (required)
- npm

### Installation & Startup

1. **Clone the repository**

   ```bash
   git clone https://github.com/ezores/smart_locker_project.git
   cd smart_locker_project
   ```

2. **Test platform compatibility (recommended)**

   ```bash
   ./test_platform_compatibility.sh
   ```

3. **Run the unified startup script:**

   ```bash
   ./start.sh --demo --reset-db --verbose
   ```

4. **Access the application:**

   - Backend API: http://localhost:5050
   - Health Check: http://localhost:5050/api/health
   - Frontend: http://localhost:5173

5. **Demo credentials:**
   - Username: `admin`
   - Password: `admin123`

### Linux/WSL Setup

If you're running on Linux or WSL and encounter issues:

1. **Install PostgreSQL (required):**

   ```bash
   ./setup_postgresql.sh
   ```

2. **Ensure PostgreSQL is running:**

   ```bash
   # Ubuntu/Debian
   sudo systemctl start postgresql
   sudo systemctl enable postgresql

   # macOS
   brew services start postgresql@14
   ```

3. **Fix npm cache issues (if needed):**

   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm cache clean --force
   npm install --force
   cd ..
   ```

4. **Ensure proper permissions:**
   ```bash
   chmod +x start.sh
   chmod +x setup_postgresql.sh
   chmod +x test_platform_compatibility.sh
   ```

### Platform Support

The system is tested and supported on:

- **macOS** (Intel & Apple Silicon)
- **Ubuntu/Debian** (20.04+, including Raspberry Pi OS)
- **CentOS/RHEL** (7+, 8+)
- **Fedora** (32+)
- **WSL** (Windows Subsystem for Linux)
- **Raspberry Pi** (3B+, 4B, 5)

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
curl http://localhost:5050/api/health

# Login
curl -X POST http://localhost:5050/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get lockers (with token from login)
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:5050/api/lockers
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
2. **Database connection issues**:
   - Ensure PostgreSQL is running (`sudo systemctl start postgresql`)
   - Check PostgreSQL connection settings
   - Verify database user permissions
3. **npm installation fails**: The script includes retry logic and cache cleaning
4. **Frontend not loading**: Check if Vite dev server is running on port 5173
5. **Virtual environment issues**: The script automatically creates and activates `.venv`

### Linux/WSL Specific Issues

1. **npm cache errors**: Use `npm install --force` or run the setup script
2. **PostgreSQL not found**: Run `./setup_postgresql.sh` to install PostgreSQL
3. **Permission denied**: Ensure scripts are executable (`chmod +x *.sh`)
4. **Virtual environment activation fails**: The script now handles multiple shell types
5. **PostgreSQL service not running**: Start with `sudo systemctl start postgresql`

### Platform-Specific Notes

#### Raspberry Pi

- Frontend compilation may be slower
- Consider using `--minimal` mode for testing
- Ensure adequate cooling for extended use
- Recommended: 2GB+ RAM, 8GB+ storage

#### WSL (Windows Subsystem for Linux)

- PostgreSQL must be installed and running
- npm may need `--force` flag
- File permissions may need adjustment
- Consider using Windows paths for better performance

#### macOS

- All features fully supported
- PostgreSQL via Homebrew
- Node.js via Homebrew or official installer

### Manual Cleanup

If the startup script fails, manually clean up:

```bash
# Kill processes on ports
lsof -ti:5172 | xargs kill -9
lsof -ti:5173 | xargs kill -9

# Clean npm cache
cd frontend && npm cache clean --force

# Restart PostgreSQL (if using)
brew services restart postgresql@14  # macOS
sudo systemctl restart postgresql    # Linux
```

## License

MIT License - see LICENSE file for details.
