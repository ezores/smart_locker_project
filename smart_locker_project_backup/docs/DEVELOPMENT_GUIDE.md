# Smart Locker System - Development Guide

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git
- A code editor (VS Code recommended)

### Development Environment Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd smart_locker_project
   ```

2. **Set up Python environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up Node.js environment**

   ```bash
   npm install
   ```

4. **Start development servers**
   ```bash
   ./start_dev.sh --demo
   ```

## Project Structure

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

## Code Style Guidelines

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Use meaningful variable and function names
- Keep functions small and focused

**Example:**

```python
from typing import List, Optional
from flask import jsonify, request
from models import User, db

def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Retrieve a user by their ID.

    Args:
        user_id: The unique identifier of the user

    Returns:
        User object if found, None otherwise
    """
    return User.query.get(user_id)

@app.route('/api/users/<int:user_id>')
def api_get_user(user_id: int):
    """Get user information by ID."""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'role': user.role
    })
```

### JavaScript/React (Frontend)

- Use functional components with hooks
- Follow ESLint and Prettier configurations
- Use meaningful component and variable names
- Keep components small and focused
- Use TypeScript for better type safety (recommended)

**Example:**

```jsx
import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useLanguage } from "../contexts/LanguageContext";

/**
 * UserProfile component displays user information
 * @param {Object} props - Component props
 * @param {string} props.userId - User ID to display
 */
const UserProfile = ({ userId }) => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserProfile(userId);
  }, [userId]);

  const fetchUserProfile = async (id) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/users/${id}`);
      const data = await response.json();
      setProfile(data);
    } catch (error) {
      console.error("Error fetching user profile:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>{t("loading")}</div>;
  }

  return (
    <div className="user-profile">
      <h2>{profile?.username}</h2>
      <p>
        {t("role")}: {profile?.role}
      </p>
    </div>
  );
};

export default UserProfile;
```

## Adding New Features

### 1. Backend API Development

1. **Create the database model** (if needed)

   ```python
   # models.py
   class NewFeature(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       name = db.Column(db.String(100), nullable=False)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
   ```

2. **Create API endpoints**

   ```python
   # app.py
   @app.route('/api/new-feature', methods=['GET'])
   def api_get_new_feature():
       """Get all new features."""
       features = NewFeature.query.all()
       return jsonify([{
           'id': f.id,
           'name': f.name,
           'created_at': f.created_at.isoformat()
       } for f in features])
   ```

3. **Add tests**
   ```python
   # tests/test_new_feature.py
   def test_get_new_feature():
       response = client.get('/api/new-feature')
       assert response.status_code == 200
       assert isinstance(response.json, list)
   ```

### 2. Frontend Component Development

1. **Create the component**

   ```jsx
   // src/components/NewFeature.jsx
   import React, { useState, useEffect } from "react";
   import { useLanguage } from "../contexts/LanguageContext";

   const NewFeature = () => {
     const { t } = useLanguage();
     const [features, setFeatures] = useState([]);

     useEffect(() => {
       fetchFeatures();
     }, []);

     const fetchFeatures = async () => {
       const response = await fetch("/api/new-feature");
       const data = await response.json();
       setFeatures(data);
     };

     return (
       <div className="new-feature">
         <h2>{t("new_feature_title")}</h2>
         {features.map((feature) => (
           <div key={feature.id}>{feature.name}</div>
         ))}
       </div>
     );
   };

   export default NewFeature;
   ```

2. **Add translations**

   ```jsx
   // src/contexts/LanguageContext.jsx
   en: {
     new_feature_title: "New Feature",
     // ... other translations
   },
   fr: {
     new_feature_title: "Nouvelle Fonctionnalité",
     // ... other translations
   }
   ```

3. **Add tests**

   ```jsx
   // src/components/__tests__/NewFeature.test.jsx
   import { render, screen } from "@testing-library/react";
   import NewFeature from "../NewFeature";

   test("renders new feature component", () => {
     render(<NewFeature />);
     expect(screen.getByText(/new feature/i)).toBeInTheDocument();
   });
   ```

## Internationalization (i18n)

### Adding New Languages

1. **Add language to the context**

   ```jsx
   // src/contexts/LanguageContext.jsx
   const availableLanguages = ["en", "fr", "es", "tr", "de"]; // Add new language

   const translations = {
     en: {
       /* English translations */
     },
     fr: {
       /* French translations */
     },
     es: {
       /* Spanish translations */
     },
     tr: {
       /* Turkish translations */
     },
     de: {
       /* German translations */
     }, // Add new language translations
   };
   ```

2. **Add language flag and name**

   ```jsx
   const languageFlags = {
     en: "🇺🇸",
     fr: "🇫🇷",
     es: "🇪🇸",
     tr: "🇹🇷",
     de: "🇩🇪", // Add new language flag
   };

   const languageNames = {
     en: "English",
     fr: "Français",
     es: "Español",
     tr: "Türkçe",
     de: "Deutsch", // Add new language name
   };
   ```

### Translation Guidelines

- Use descriptive keys: `user_profile_title` instead of `title`
- Group related translations: `user_management`, `equipment_management`
- Keep translations concise and clear
- Test translations in context
- Consider cultural differences

## Testing

### Backend Testing

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_api.py

# Run with coverage
python -m pytest --cov=app tests/
```

### Frontend Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

### Test Guidelines

- Write tests for all new features
- Test both success and error cases
- Mock external dependencies
- Use descriptive test names
- Keep tests focused and independent

## Database Migrations

### Creating Migrations

```bash
# Create a new migration
flask db migrate -m "Add new feature table"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

### Migration Guidelines

- Always create migrations for schema changes
- Test migrations on development data
- Include rollback instructions
- Document breaking changes

## Security Best Practices

### Backend Security

- Validate all inputs
- Use parameterized queries
- Implement rate limiting
- Sanitize user data
- Use HTTPS in production
- Keep dependencies updated

### Frontend Security

- Sanitize user inputs
- Use HTTPS for API calls
- Implement proper authentication
- Validate data on client side
- Use Content Security Policy

## Performance Optimization

### Backend Optimization

- Use database indexes
- Implement caching
- Optimize database queries
- Use connection pooling
- Monitor performance metrics

### Frontend Optimization

- Lazy load components
- Optimize bundle size
- Use React.memo for expensive components
- Implement proper error boundaries
- Use service workers for caching

## Deployment

### Development Deployment

```bash
# Start development servers
./start_dev.sh

# Build frontend for production
npm run build

# Start production backend
python app.py --port 5050
```

### Production Deployment

1. **Set up production environment**

   ```bash
   export FLASK_ENV=production
   export JWT_SECRET_KEY=your-secret-key
   ```

2. **Build frontend**

   ```bash
   npm run build
   ```

3. **Set up reverse proxy (nginx)**

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:5050;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Use production WSGI server**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5050 app:app
   ```

## Troubleshooting

### Common Issues

1. **Import errors**

   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

2. **Database issues**

   - Check database file permissions
   - Run migrations: `flask db upgrade`

3. **Frontend build errors**

   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check for syntax errors in components

4. **API connection issues**
   - Verify backend is running on correct port
   - Check CORS configuration
   - Verify proxy settings in vite.config.js

### Debugging

- Use Flask debug mode for backend debugging
- Use React Developer Tools for frontend debugging
- Check browser console for JavaScript errors
- Monitor network requests in browser dev tools

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Commit your changes: `git commit -m "Add new feature"`
7. Push to the branch: `git push origin feature/new-feature`
8. Submit a pull request

## Code Review Guidelines

- Review for functionality and edge cases
- Check for security vulnerabilities
- Ensure proper error handling
- Verify translations are complete
- Test in multiple browsers
- Check for performance issues
- Ensure accessibility standards are met

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [JWT Documentation](https://jwt.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
