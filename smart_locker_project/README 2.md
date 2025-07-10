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

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd smart_locker_project
   ```

2. **Set up the backend**

   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up the frontend**

   ```bash
   # Install dependencies
   npm install
   ```

4. **Start the development servers**

   ```bash
   # Start both backend and frontend
   ./scripts/start_dev.sh

   # Or start individually:
   # Backend: python backend/app.py --port 5050 --demo
   # Frontend: cd frontend && npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5050

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
FLASK_ENV=development
JWT_SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///smart_locker.db
```

### Database Setup

The system uses SQLite by default. For production, consider using PostgreSQL or MySQL.

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

### Authentication Endpoints

- `POST /api/auth/login` - User login
- `GET /api/user/profile` - Get user profile

### Equipment Management

- `GET /api/items` - List all items
- `POST /api/borrow` - Borrow equipment
- `POST /api/return` - Return equipment

### Administrative Endpoints

- `GET /api/admin/stats` - System statistics
- `GET /api/admin/users` - User management
- `GET /api/admin/logs` - Activity logs
- `POST /api/admin/export` - Export reports

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
- API: RESTful design principles

### Adding New Features

1. Create feature branch
2. Implement backend API endpoints
3. Create frontend components
4. Add translations for all supported languages
5. Write tests
6. Update documentation

## 🌍 Internationalization

The system supports multiple languages:

- English (en)
- French (fr)
- Spanish (es)
- Turkish (tr)

To add a new language:

1. Add translations to `src/contexts/LanguageContext.jsx`
2. Update language selector component
3. Test all UI elements

## 🎨 Theming

### Dark Mode Support

- Automatic theme detection
- Manual theme toggle
- Consistent styling across all components
- Proper contrast ratios

### Customization

- Primary colors in `tailwind.config.js`
- Component styling in individual files
- Global styles in `src/index.css`

## 📈 Monitoring and Logging

### Activity Logging

- User login/logout events
- Equipment borrow/return transactions
- Administrative actions
- System errors and warnings

### Export Capabilities

- Excel reports (.xlsx)
- PDF reports (.pdf)
- CSV data export (.csv)
- Custom date range filtering

## 🔒 Security Features

- JWT token authentication
- Password hashing with bcrypt
- Role-based access control
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## 🚀 Deployment

### Production Setup

1. Set up production database
2. Configure environment variables
3. Set up reverse proxy (nginx)
4. Configure SSL certificates
5. Set up monitoring and logging

### Docker Deployment

```bash
# Build and run with Docker
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the documentation
- Review the code comments

## 🔄 Version History

### v1.0.0 (Current)

- Initial release
- Core functionality implemented
- Multi-language support
- Dark mode support
- Comprehensive logging
- Export capabilities

---

**Built with ❤️ using Flask and React**
