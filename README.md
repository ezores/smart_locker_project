# Smart Locker System

A modern locker management system with Flask backend and React frontend, featuring RFID authentication, real-time monitoring, and comprehensive reporting.

## Features

- **Secure Authentication**: RFID card-based access with user management
- **Real-time Monitoring**: Live locker status and usage tracking
- **Multi-language Support**: English, French, Spanish, and Turkish
- **Admin Dashboard**: Comprehensive analytics and user management
- **Reporting System**: Export capabilities for usage reports
- **Modern UI**: Responsive React frontend with dark mode support

## Quick Start

### Prerequisites

- **macOS/Linux** (Windows support coming soon)
- **Python 3.8+**
- **Node.js 16+**
- **Homebrew** (macOS) or **apt** (Linux)

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/smart-locker-system.git
   cd smart-locker-system
   ```

2. **Set up database credentials** (optional):

   ```bash
   # Create a .env file for custom credentials
   echo "DB_NAME=my_locker_db" > .env
   echo "DB_USER=my_locker_user" >> .env
   echo "DB_PASS=my_secure_password" >> .env
   ```

3. **Run the automated setup**:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

The script will automatically:

- Install PostgreSQL if not present
- Create database and user
- Install Python and Node.js dependencies
- Start backend (port 5172) and frontend (port 5173)

### Default Credentials

**Database**:

- Host: `localhost`
- Port: `5432`
- Database: `smart_locker_db`
- User: `smart_locker_user`
- Password: `smartlockerpass123`

**Application**:

- Admin: `admin` / `admin123`
- Student: `student1` / `student123`

## Development

### Running Tests

```bash
./start.sh --test
```

This will run comprehensive backend API tests and frontend tests.

### Manual Setup

If you prefer manual setup:

1. **Install PostgreSQL**:

   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql

   # Linux
   sudo apt-get install postgresql postgresql-contrib
   sudo service postgresql start
   ```

2. **Create database**:

   ```bash
   psql -U postgres -c "CREATE DATABASE smart_locker_db;"
   psql -U postgres -c "CREATE USER smart_locker_user WITH PASSWORD 'smartlockerpass123';"
   psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE smart_locker_db TO smart_locker_user;"
   ```

3. **Set up Python environment**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Set up Node.js environment**:

   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Start services**:

   ```bash
   # Backend
   source .venv/bin/activate
   cd backend
   python app.py --port 5172 --demo --reset-db --verbose

   # Frontend (new terminal)
   cd frontend
   npm run dev
   ```

## Environment Variables

You can customize the database configuration using environment variables:

```bash
export DB_NAME="my_custom_db"
export DB_USER="my_custom_user"
export DB_PASS="my_secure_password"
export DB_PORT="5432"
export DB_HOST="localhost"
```

## API Documentation

### Authentication

- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Admin Endpoints

- `GET /api/admin/active-borrows` - Get active borrows
- `GET /api/admin/users` - Get all users
- `GET /api/admin/stats` - Get system statistics

### Locker Management

- `GET /api/lockers` - Get all lockers
- `POST /api/lockers/borrow` - Borrow an item
- `POST /api/lockers/return` - Return an item

## Project Structure

```
smart_locker_project/
├── backend/                 # Flask API server
│   ├── api/                # API routes
│   ├── models.py           # Database models
│   ├── demo_data.py        # Demo data generation
│   ├── app.py              # Main Flask application
│   └── tests/              # Backend tests
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   └── contexts/       # React contexts
│   └── package.json
├── data/                   # Data files
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── start.sh               # Automated setup script
```

## Security Considerations

### Database Security

- Default credentials are for development only
- Use strong passwords in production
- Consider using environment variables for production
- Enable SSL connections for production databases

### Application Security

- JWT tokens for authentication
- Input validation on all endpoints
- CORS configuration for frontend
- Rate limiting on sensitive endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `./start.sh --test`
6. Submit a pull request

## Troubleshooting

### Common Issues

**PostgreSQL Connection Failed**:

```bash
# Check if PostgreSQL is running
brew services list | grep postgresql
# Start if needed
brew services start postgresql
```

**Port Already in Use**:

```bash
# Find process using port
lsof -i :5172
# Kill process
kill -9 <PID>
```

**Python Dependencies**:

```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Node.js Dependencies**:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the API documentation
3. Open an issue on GitHub
4. Contact the development team
