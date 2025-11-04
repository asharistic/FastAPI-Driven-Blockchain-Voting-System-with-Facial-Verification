# Blockchain Voting System - React Frontend

This is the React frontend for the Blockchain Voting System. It provides a modern, responsive user interface for both voters and administrators.

## Features

### User Pages
- **Home**: Welcome page with system overview and features
- **Register**: Voter registration with facial capture
- **Vote**: Face verification and candidate selection

### Admin Pages
- **Admin Login**: Secure authentication
- **Dashboard**: Overview with statistics and results
- **Elections Management**: Create and manage elections
- **Candidates Management**: Add and manage candidates
- **Voters Management**: View and manage registered voters
- **Blockchain Viewer**: View the entire blockchain ledger
- **Results Viewer**: View voting results with charts

## Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Build for production**
   ```bash
   npm run build
   ```

## Configuration

The frontend is configured to connect to the backend API. Update the API URL in:
- `src/services/api.js` - Change `API_BASE_URL` or set `VITE_API_URL` environment variable

Default backend URL: `http://127.0.0.1:5000`

## Project Structure

```
Frontend/
├── src/
│   ├── components/
│   │   ├── Layout.jsx          # Main layout component
│   │   ├── ProtectedRoute.jsx  # Route protection
│   │   └── admin/              # Admin components
│   ├── pages/
│   │   ├── Home.jsx            # Home page
│   │   ├── Register.jsx       # Registration page
│   │   ├── Vote.jsx            # Voting page
│   │   └── admin/              # Admin pages
│   ├── services/
│   │   └── api.js              # API service layer
│   ├── App.jsx                 # Main app component
│   ├── main.jsx                # Entry point
│   └── index.css               # Global styles
├── package.json
└── vite.config.js
```

## Styling

The frontend uses a black and gold theme with:
- CSS Variables for consistent theming
- Responsive design for mobile devices
- Modern UI components with glassmorphism effects

## API Integration

All API calls are handled through the `api.js` service layer which:
- Manages authentication tokens
- Handles request/response interceptors
- Provides organized API methods

## Notes

- The frontend uses React Router for navigation
- Authentication tokens are stored in localStorage
- Camera access is required for registration and voting
- The admin panel is protected by JWT authentication
