# Smart Locker System

A modern locker management system with Flask backend and React frontend, featuring RFID authentication, real-time monitoring, and comprehensive reporting.

## Features

- Secure Authentication: RFID card-based access with user management
- Locker Reservations: Advanced reservation system with time-based access
- Real-time Monitoring: Live locker status and usage tracking
- Multi-language Support: English, French, Spanish, and Turkish
- Admin Dashboard: Comprehensive analytics and user management
- Reporting System: Export capabilities for usage reports
- Modern UI: Responsive React frontend with dark mode support

## Quick Start

### Prerequisites

- macOS/Linux (Windows support coming soon)
- Python 3.8+
- Node.js 16+
- pip3
- npm
- PostgreSQL
- tmux (optional, for split-pane view)

> The `start.sh` script will check for all required dependencies and print clear error messages if any are missing. Please install all required dependencies before running the script.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/smart-locker-system.git
   cd smart-locker-system
   ```

2. Set up database credentials (optional):

   ```bash
   # Create a .env file for custom credentials
   echo "DB_NAME=my_locker_db" > .env
   echo "DB_USER=my_locker_user" >> .env
   echo "DB_PASS=my_secure_password" >> .env
   ```

3. Run the automated setup:
   ```bash
   chmod +x start.sh
   ./start.sh --demo
   ```

The script will automatically:

- Install Python and Node.js dependencies
- Set up the database and user
- Start backend (port 5172) and frontend (port 5173)
- Check for all required dependencies

### Troubleshooting

- If you see errors about missing dependencies, install them using your OS package manager or from the official websites:
  - Python: https://www.python.org/downloads/
  - Node.js: https://nodejs.org/en/download/
  - PostgreSQL: https://www.postgresql.org/download/
  - tmux (optional): https://github.com/tmux/tmux/wiki
- If the backend or frontend fails to start, check the logs in the terminal for error messages.
- Ensure PostgreSQL is running and accessible.
- Check your `DATABASE_URL` in `.env` or the script output.
- Try running `psql $DATABASE_URL` to test your database connection.
- For frontend issues, try running `npm install` and `npm run dev` in the `frontend` directory manually.

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
- Manager: `manager` / `manager123`
- Supervisor: `supervisor` / `supervisor123`

## Development

### Running Tests

```bash
./start.sh --test
```

This will run backend API tests and frontend tests.

### Manual Setup

If you prefer manual setup:

1. Install PostgreSQL:

   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql

   # Linux
   sudo apt-get install postgresql postgresql-contrib
   sudo service postgresql start
   ```

2. Create database:

   ```bash
   psql -U postgres -c "CREATE DATABASE smart_locker_db;"
   psql -U postgres -c "CREATE USER smart_locker_user WITH PASSWORD 'smartlockerpass123';"
   psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE smart_locker_db TO smart_locker_user;"
   ```

3. Set up Python environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Set up Node.js environment:

   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. Start services:

   ```bash
   # Backend
   source .venv/bin/activate
   cd backend
   python app.py --port 5172 --demo --verbose

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

- POST /api/auth/login - User login
- POST /api/auth/logout - User logout

### Admin Endpoints

- GET /api/admin/active-borrows - Get active borrows
- GET /api/admin/users - Get all users
- GET /api/admin/stats - Get system statistics
- GET /api/admin/export/reservations - Export reservations data

### Locker Management

- GET /api/lockers - Get all lockers
- POST /api/lockers/borrow - Borrow an item
- POST /api/lockers/return - Return an item

### Reservation System

- GET /api/reservations - Get user reservations (admin sees all)
- POST /api/reservations - Create new reservation
- PUT /api/reservations/{id} - Update reservation
- POST /api/reservations/{id}/cancel - Cancel reservation
- POST /api/reservations/access/{code} - Access with code
- POST /api/reservations/rfid-access/{tag} - Access with RFID

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

## Reservation System

The Smart Locker System now includes a comprehensive reservation system with the following features:

### Key Features

- Time-based Access: Reservations can be made for specific time windows (max 24 hours)
- Unique Access Codes: Each reservation gets a unique 8-digit access code
- RFID Integration: Users can access their reservations using RFID cards
- Calendar Interface: Interactive calendar view showing all reservations
- Conflict Prevention: System prevents double-booking of lockers
- Export Capabilities: Export reservations to CSV, Excel, or PDF
- Multi-language Support: Full translation support for all reservation features

### Reservation Workflow

1. Create Reservation: Users select a locker and time window
2. Access Control: Users can access lockers using:
   - Unique 8-digit access code
   - RFID card (if user has active reservation)
3. Time Validation: System ensures access only during reserved time
4. Modification: Users can modify or cancel active reservations
5. Logging: All reservation activities are logged for audit purposes

### Access Methods

- Web Interface: Users can view and manage reservations through the web UI
- Access Codes: Physical access using 8-digit codes
- RFID Cards: Automatic access when RFID card is scanned
- Admin Management: Admins can manage all reservations

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
- Reservation access codes are unique and secure
- Rate limiting on sensitive endpoints
