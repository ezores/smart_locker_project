# Smart Locker Management System

A comprehensive smart locker management system built with **Flask** (backend) and **React** (frontend), designed for deployment on Raspberry Pi 5 with full hardware integration capabilities.

## 🚀 Features

### Backend (Flask)

- **Authentication System**: JWT-based authentication with role-based access
- **Database Management**: SQLite with SQLAlchemy ORM
- **Hardware Integration**: RFID reader and RS485 communication support
- **Internationalization**: Multi-language support (EN, FR, ES, TR)
- **RESTful API**: Complete API for React frontend integration
- **Logging System**: Comprehensive activity logging and CSV export

### Frontend (React)

- **Modern UI/UX**: Clean, responsive design with Tailwind CSS
- **Real-time Updates**: Live data synchronization with backend
- **Mobile-First**: Optimized for touch interfaces
- **Internationalization**: Full i18n support matching backend
- **Role-based Interface**: Different UIs for users and administrators

## 🛠 Tech Stack

### Backend

- **Python 3.8+** with Flask framework
- **SQLAlchemy** for database management
- **Flask-Babel** for internationalization
- **PyJWT** for authentication
- **pyserial** for hardware communication

### Frontend

- **React 18** with modern hooks
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Axios** for API communication

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- pip (Python package manager)
- npm (Node.js package manager)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd smart_locker_project
```

### 2. Backend Setup (Flask)

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python app.py --port 8080
```

### 3. Frontend Setup (React)

```bash
# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

### 4. Access the Application

- **React Frontend**: http://localhost:3000 (main application)
- **Flask Backend API**: http://localhost:8080/api/\* (API endpoints)
- **Flask Templates**: http://localhost:8080 (traditional interface)

## 🔐 Authentication

### Default Credentials

| Username   | Password      | Role     | Access                         |
| ---------- | ------------- | -------- | ------------------------------ |
| `admin`    | `admin123`    | Admin    | Full system access             |
| `employee` | `employee123` | Employee | Basic borrow/return operations |

### Role Permissions

- **Admin**: Full access to all features including user management, system configuration, and reports
- **Employee**: Can borrow and return items, view their own history

## 🌍 Internationalization

The system supports multiple languages:

- **English** (en) - Default
- **French** (fr)
- **Spanish** (es)
- **Turkish** (tr)

Language can be changed via the UI language selector or API endpoints.

## 📱 API Endpoints

### Authentication

- `POST /api/auth/login` - User login
- `GET /api/user/profile` - Get user profile

### Items & Lockers

- `GET /api/items` - List all items
- `GET /api/lockers` - List all lockers
- `POST /api/borrow` - Borrow an item
- `POST /api/return` - Return an item

### Admin

- `GET /api/admin/stats` - System statistics
- `GET /api/admin/recent-activity` - Recent activity logs

## 🏗 Project Structure

```
smart_locker_project/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── requirements-pi.txt    # Raspberry Pi specific dependencies
├── package.json           # Node.js dependencies
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── src/                   # React source code
│   ├── components/        # Reusable React components
│   ├── contexts/          # React context providers
│   ├── pages/             # Page components
│   └── main.jsx           # React entry point
├── templates/             # Flask HTML templates
├── static/                # Static files (CSS, images)
├── translations/          # Babel translation files
├── db/                    # SQLite database
└── utils/                 # Utility functions
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for production:

```env
FLASK_SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
DATABASE_URL=sqlite:///path/to/database.db
```

### Hardware Configuration

For Raspberry Pi deployment, install additional dependencies:

```bash
pip install -r requirements-pi.txt
```

## 🚀 Deployment

### Development

1. **Backend**: `python app.py --port 8080`
2. **Frontend**: `npm run dev`

### Production

1. **Build Frontend**: `npm run build`
2. **Serve Static Files**: Copy `dist/` to Flask's static directory
3. **Use Production WSGI**: Gunicorn or uWSGI

### Raspberry Pi Deployment

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pip nodejs npm

# Setup the application
cd smart_locker_project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-pi.txt
npm install
npm run build

# Run as service
sudo systemctl enable smart-locker
sudo systemctl start smart-locker
```

## 🔒 Security Features

- JWT-based authentication
- Password hashing with Werkzeug
- Role-based access control
- Input validation and sanitization
- CORS configuration for API
- Secure session management

## 📊 Monitoring & Logging

- Comprehensive activity logging
- CSV export functionality
- Real-time system statistics
- Error tracking and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is developed for LACIME and is proprietary software.

## 🆘 Support

For technical support or questions:

- Check the documentation
- Review the API endpoints
- Check the logs in the `db/` directory
- Ensure all dependencies are installed

## 🔄 Updates

To update the system:

```bash
# Backend
pip install -r requirements.txt --upgrade

# Frontend
npm update
npm run build
```

---

**Built with ❤️ for LACIME Smart Locker System**
