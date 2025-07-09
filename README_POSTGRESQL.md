# Smart Locker System - PostgreSQL Migration

This document describes the migration from SQLite to PostgreSQL and the new comprehensive startup system.

## Overview

The Smart Locker System has been migrated from SQLite to PostgreSQL for better scalability, performance, and enterprise features. The system now includes:

- PostgreSQL database with comprehensive data models
- Enhanced startup script with multiple environment support
- Comprehensive demo data generation
- Health check endpoints
- Multiple deployment modes

## Quick Start

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
- `--port PORT`: Backend port (default: 5050)
- `--frontend-port PORT`: Frontend port (default: 5173)

### Database Options

- `--db-host HOST`: Database host (default: localhost)
- `--db-port PORT`: Database port (default: 5432)
- `--db-name NAME`: Database name (default: smart_locker)
- `--db-user USER`: Database user (default: postgres)
- `--db-password PASS`: Database password (default: postgres)

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

## API Endpoints

### Health Check

- `GET /api/health`: System health status and database connection

### Authentication

- `POST /api/auth/login`: User login
- `GET /api/user/profile`: User profile information

### Items and Lockers

- `GET /api/items`: List all items
- `GET /api/lockers`: List all lockers
- `POST /api/borrow`: Borrow an item
- `POST /api/return`: Return an item

### Admin Functions

- `GET /api/admin/stats`: System statistics
- `GET /api/admin/recent-activity`: Recent activity
- `GET /api/admin/active-borrows`: Currently borrowed items
- `GET /api/admin/reports`: Generate reports
- `GET /api/admin/export`: Export data in various formats

## Environment Variables

The system uses the following environment variables for database configuration:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=smart_locker
export DB_USER=postgres
export DB_PASSWORD=postgres
```

## Demo Credentials

### Admin Users

- Username: `admin`, Password: `admin123`
- Username: `manager`, Password: `manager123`

### Student Users

- Username: `student1` through `student10`, Password: `student123`

## Troubleshooting

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
./start.sh --dev --demo --port 5051 --frontend-port 5174
```

### Verbose Debugging

Enable verbose mode for detailed logging:

```bash
./start.sh --dev --demo --verbose
```

## Migration Notes

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

## Development

### Adding New Models

1. Update `models.py` with new model definitions
2. Add to the `init_models()` function return tuple
3. Update demo data generation if needed
4. Test with `./start.sh --dev --reset-db --verbose`

### Database Migrations

For production deployments, consider using Alembic for database migrations:

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Production Deployment

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
