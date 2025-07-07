# Smart Locker System - React Frontend

A modern, responsive React frontend for the Smart Locker Management System built with Vite, Tailwind CSS, and React Router.

## Features

- 🎨 **Modern UI/UX**: Clean, professional design with smooth animations
- 📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- 🌍 **Internationalization**: Support for English, French, Spanish, and Turkish
- 🔐 **Authentication**: Secure login with JWT tokens
- 👥 **Role-based Access**: Different interfaces for users and administrators
- 🎯 **Interactive Components**: Modern form controls, modals, and navigation
- ⚡ **Fast Development**: Built with Vite for lightning-fast development experience

## Tech Stack

- **React 18** - Modern React with hooks and functional components
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client for API communication
- **Lucide React** - Beautiful, customizable icons
- **Context API** - State management for auth and language

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- The Flask backend running on port 8080

### Installation

1. **Install dependencies:**

   ```bash
   npm install
   ```

2. **Start the development server:**

   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Header.jsx      # Navigation header with language selector
│   ├── ProtectedRoute.jsx  # Route protection for authenticated users
│   └── AdminRoute.jsx  # Route protection for admin users
├── contexts/           # React Context providers
│   ├── AuthContext.jsx # Authentication state management
│   └── LanguageContext.jsx # Internationalization
├── pages/              # Page components
│   ├── Login.jsx       # Authentication page
│   ├── MainMenu.jsx    # Main navigation menu
│   ├── Borrow.jsx      # Item borrowing workflow
│   ├── Return.jsx      # Item return workflow
│   ├── AdminDashboard.jsx # Admin overview dashboard
│   ├── Users.jsx       # User management (placeholder)
│   ├── Items.jsx       # Item management (placeholder)
│   ├── Lockers.jsx     # Locker management (placeholder)
│   └── Logs.jsx        # System logs (placeholder)
├── App.jsx             # Main application component
├── main.jsx            # Application entry point
└── index.css           # Global styles and Tailwind imports
```

## Key Features

### Authentication System

- JWT token-based authentication
- Automatic token refresh
- Protected routes for authenticated users
- Admin-only routes for administrative functions

### Internationalization

- Support for 4 languages: English, French, Spanish, Turkish
- Language persistence in localStorage
- Flag-based language selector in header
- Complete translation coverage for all UI elements

### Modern UI Components

- **Header**: Responsive navigation with mobile menu
- **Cards**: Consistent card layouts with hover effects
- **Buttons**: Primary and secondary button styles
- **Forms**: Modern form inputs with validation
- **Loading States**: Spinner components for async operations

### Responsive Design

- Mobile-first approach
- Breakpoint-based layouts
- Touch-friendly interface
- Optimized for various screen sizes

## API Integration

The frontend communicates with the Flask backend through:

- **Base URL**: `http://localhost:8080` (configured in Vite proxy)
- **Authentication**: JWT tokens in Authorization header
- **Error Handling**: Consistent error display across all API calls
- **Loading States**: Visual feedback during API operations

## Development Workflow

### Adding New Pages

1. Create a new component in `src/pages/`
2. Add the route to `src/App.jsx`
3. Add navigation links in `src/components/Header.jsx`
4. Add translations to `src/contexts/LanguageContext.jsx`

### Adding New Components

1. Create the component in `src/components/`
2. Use Tailwind CSS for styling
3. Follow the existing component patterns
4. Add proper TypeScript-like prop validation

### Styling Guidelines

- Use Tailwind CSS utility classes
- Follow the established color scheme (primary, secondary, gray variants)
- Maintain consistent spacing and typography
- Use the predefined component classes (`.btn-primary`, `.card`, etc.)

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Configuration

### Vite Configuration (`vite.config.js`)

- React plugin for JSX support
- Development server on port 3000
- API proxy to Flask backend on port 8080
- Build output to `dist` directory

### Tailwind Configuration (`tailwind.config.js`)

- Custom color palette with primary and secondary colors
- Custom animations and keyframes
- Inter font family
- Responsive breakpoints

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance Optimizations

- Code splitting with React Router
- Lazy loading of components
- Optimized bundle size with Vite
- Efficient re-renders with React hooks
- Minimal CSS with Tailwind's purge

## Security Considerations

- JWT tokens stored in localStorage
- Automatic token cleanup on logout
- Protected routes prevent unauthorized access
- Input validation on forms
- XSS protection with React's built-in escaping

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change the port in `vite.config.js`
2. **API connection**: Ensure Flask backend is running on port 8080
3. **Build errors**: Clear `node_modules` and reinstall dependencies
4. **Styling issues**: Check Tailwind CSS configuration

### Development Tips

- Use React DevTools for debugging
- Check browser console for API errors
- Use Tailwind CSS IntelliSense extension
- Monitor network tab for API calls

## Contributing

1. Follow the existing code style
2. Add proper error handling
3. Include loading states for async operations
4. Test on multiple screen sizes
5. Update translations for new text

## License

This project is part of the Smart Locker System developed for LACIME.
