# Smart Locker Management System

A comprehensive smart locker management system built with **Flask** (backend) and **React** (frontend), designed for deployment on Raspberry Pi 5 with full hardware integration capabilities.

---

## 🚀 Features

### Backend (Flask)

- JWT-based authentication with role-based access
- SQLite with SQLAlchemy ORM
- Hardware integration (RFID, RS485)
- Multi-language support (EN, FR, ES, TR)
- RESTful API for React frontend
- Activity logging and CSV export

### Frontend (React)

- Modern, responsive UI (Tailwind CSS)
- Real-time updates
- Mobile-first design
- Full i18n support
- Role-based interface (admin/user)

---

## 🛠 Tech Stack

- **Backend:** Python 3.8+ (Flask, SQLAlchemy, Flask-Babel, PyJWT, pyserial)
- **Frontend:** React 18, Vite, Tailwind CSS, React Router, Axios

---

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- npm (or yarn)

---

## ⚡ Quick Start (Recommended)

### 1. Clone the repository

```bash
git clone <repository-url>
cd smart_locker_project
```

### 2. Use the Startup Script

```bash
./start_dev.sh
```

This will:

- Create/activate Python virtual environment
- Install Python dependencies
- Install Node.js dependencies
- Start Flask backend on port 5050
- Start React frontend on port 5173

### 3. Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:5050/api/\*

---

## 🖐 Manual Setup (Alternative)

### Backend (Flask)

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py --port 5050
```

### Frontend (React)

```bash
npm install
npm run dev
```

---

## 🔐 Authentication

### Default Credentials

| Username   | Password      | Role     |
| ---------- | ------------- | -------- |
| `admin`    | `admin123`    | Admin    |
| `employee` | `employee123` | Employee |

- **Admin:** Full access to all features
- **Employee:** Can borrow/return items, view own history

---

## 🌍 Internationalization

- English (en, default)
- French (fr)
- Spanish (es)
- Turkish (tr)

---

## 📱 API Endpoints (Sample)

- `POST /api/auth/login` - User login
- `GET /api/user/profile` - Get user profile
- `GET /api/items` - List all items
- `GET /api/lockers` - List all lockers
- `POST /api/borrow` - Borrow an item
- `POST /api/return` - Return an item
- `GET /api/admin/stats` - System statistics
- `GET /api/admin/recent-activity` - Recent activity logs

---

## 🏗 Project Structure

```
smart_locker_project/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
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
├── utils/                 # Utility functions
├── start_dev.sh           # Dev startup script
└── ...
```

---

## ⚙️ Configuration & Environment

- Environment variables: `.env` (see example in code)
- For Raspberry Pi: use `requirements-pi.txt`

---

## 🧑‍💻 Development Notes

- Flask backend uses SQLite at `db/locker.db`
- React frontend uses Vite (port 5173)
- CORS is enabled for local dev
- JWT authentication for API
- Vite proxy is set to `http://localhost:5050` for `/api` routes

---

## 🐞 Troubleshooting

### Import Errors

- Ensure you're in the virtual environment: `source .venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use

- Backend: Use `python app.py --port <different_port>`
- Frontend: Vite will suggest an alternative port if 5173 is busy

### Database Issues

- The Flask app auto-creates the DB on first run
- Ensure `db/` exists and is writable

---

## 🚀 Production & Deployment

### Build Frontend

```bash
npm run build
```

- Copy `dist/` to Flask's static directory for production serving

### Use Production WSGI

- Use Gunicorn or uWSGI for Flask in production

### Raspberry Pi

```bash
pip install -r requirements-pi.txt
```

---

## 🏁 Startup Script Details (`start_dev.sh`)

- Checks/creates Python virtual environment
- Installs Python and Node.js dependencies
- Starts Flask backend (port 5050)
- Starts React frontend (port 5173)
- Cleans up both servers on exit

---

## 📞 Support

If you have issues, please check the troubleshooting section above or open an issue.
