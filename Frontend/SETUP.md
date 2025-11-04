# React Frontend Setup Guide

## Quick Start

1. **Navigate to Frontend directory**
   ```powershell
   cd Frontend
   ```

2. **Install dependencies** (if not already done)
   ```powershell
   npm install
   ```

3. **Start development server**
   ```powershell
   npm run dev
   ```

4. **Access the application**
   - Frontend will run on: `http://localhost:3000`
   - Make sure your backend is running on: `http://127.0.0.1:5000`

## Project Structure

```
Frontend/
├── src/
│   ├── components/
│   │   ├── Layout.jsx                    # Main layout with header/nav/footer
│   │   ├── Layout.css
│   │   ├── ProtectedRoute.jsx           # Admin route protection
│   │   └── admin/
│   │       ├── DashboardOverview.jsx   # Dashboard stats & overview
│   │       ├── ElectionsManagement.jsx   # CRUD for elections
│   │       ├── CandidatesManagement.jsx # CRUD for candidates
│   │       ├── VotersManagement.jsx     # View/manage voters
│   │       ├── BlockchainViewer.jsx     # Blockchain ledger viewer
│   │       └── ResultsViewer.jsx       # Voting results display
│   ├── pages/
│   │   ├── Home.jsx                     # Home page
│   │   ├── Home.css
│   │   ├── Register.jsx                 # Voter registration
│   │   ├── Register.css
│   │   ├── Vote.jsx                     # Voting interface
│   │   ├── Vote.css
│   │   └── admin/
│   │       ├── AdminLogin.jsx           # Admin login page
│   │       ├── AdminLogin.css
│   │       ├── AdminDashboard.jsx       # Main admin dashboard
│   │       └── AdminDashboard.css
│   ├── services/
│   │   └── api.js                       # API service layer
│   ├── App.jsx                          # Main app with routing
│   ├── main.jsx                         # React entry point
│   └── index.css                        # Global styles & theme
├── package.json
├── vite.config.js
└── README.md
```

## Features Implemented

### User Interface
✅ Home page with features and information
✅ Registration page with camera capture
✅ Voting page with face verification and candidate selection
✅ Responsive design for mobile devices

### Admin Interface
✅ Admin login with authentication
✅ Dashboard with statistics overview
✅ Elections management (Create, Read, Delete)
✅ Candidates management (Create, Read, Delete)
✅ Voters management (Read, Delete)
✅ Blockchain viewer
✅ Results viewer with percentage bars

### Technical Features
✅ React Router for navigation
✅ Protected routes for admin
✅ API service layer with axios
✅ JWT token management
✅ Error handling and loading states
✅ Black & Gold theme throughout

## API Connection

The frontend is configured to connect to your FastAPI backend. The API base URL is set in `src/services/api.js`:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000'
```

You can override this by setting the `VITE_API_URL` environment variable.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Next Steps

1. **Start the backend server** (if not running):
   ```powershell
   cd ..
   uvicorn backend.main:app --host 127.0.0.1 --port 5000 --reload
   ```

2. **Start the frontend**:
   ```powershell
   cd Frontend
   npm run dev
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://127.0.0.1:5000

## Notes

- The frontend uses Vite for fast development
- All API calls go through the service layer
- Authentication tokens are stored in localStorage
- Camera access is required for registration and voting features
- The admin panel requires JWT authentication

