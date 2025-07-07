# Smart Locker System - Development Setup

This project consists of a Flask backend API and a React frontend.

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## Quick Start

### Option 1: Using the startup script (Recommended)

```bash
./start_dev.sh
```

This will:

- Create/activate Python virtual environment
- Install Python dependencies
- Install Node.js dependencies
- Start Flask backend on port 5050
- Start React frontend on port 5173

### Option 2: Manual setup

#### Backend Setup

1. Create and activate virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Start Flask server:

```bash
python app.py --port 5050
```

#### Frontend Setup

1. Install Node.js dependencies:

```bash
npm install
```

2. Start React development server:

```bash
npm run dev
```

## Access Points

- **Backend API**: http://localhost:5050
- **Frontend**: http://localhost:5173
- **API Documentation**: Available at `/api/` endpoints

## Development Notes

- The Flask backend uses SQLite database stored in `db/locker.db`
- React frontend uses Vite for fast development
- CORS is enabled for local development
- JWT authentication is implemented for API access

## Troubleshooting

### Import Errors

If you see import errors for `jwt` or `flask_cors`:

1. Make sure you're in the virtual environment: `source .venv/bin/activate`
2. Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use

If port 5050 or 5173 is already in use:

- Backend: Use `python app.py --port <different_port>`
- Frontend: Vite will automatically suggest an alternative port

### Database Issues

If the database doesn't exist:

- The Flask app will automatically create it on first run
- Check that the `db/` directory exists and is writable
