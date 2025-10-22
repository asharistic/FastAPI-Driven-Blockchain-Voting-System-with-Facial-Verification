# Blockchain Voting System with Facial Verification

## Project Overview
A FastAPI-based blockchain voting system with facial verification for a university final year project. Features voter registration with face capture, facial verification before voting, secure vote storage in a custom blockchain, and a futuristic 3D admin dashboard with glassmorphism design.

## Tech Stack
- **Backend**: FastAPI (Python 3.11)
- **Authentication**: JWT tokens (python-jose)
- **Database**: SQLite with SQLAlchemy
- **Face Detection**: OpenCV with Haar Cascade
- **Frontend**: Tailwind CSS (via CDN), Three.js for 3D visualization
- **Charts**: Chart.js for data visualization
- **Blockchain**: Custom Python implementation

## Recent Changes
- **2025-10-22 (Latest)**: Added JWT authentication and 3D admin dashboard
  - Implemented JWT-based authentication system for admin access
  - Created stunning 3D admin login page with glassmorphism and animated gradient background
  - Built futuristic admin dashboard with Three.js blockchain visualization
  - Added Election model for managing multiple elections
  - Implemented full CRUD operations for elections, candidates, and voters
  - Integrated Chart.js for voting results and participation visualization
  - Used Tailwind CSS with dark theme, neon accents, and glassmorphism effects
  - Secure password hashing using pbkdf2_sha256 (production-ready)

- **2025-10-22 (Initial)**: Initial project setup
  - Created complete FastAPI backend with all routes
  - Implemented simple blockchain with hash chaining
  - Built face detection system using OpenCV
  - Created all HTML templates and static assets
  - Added sample candidates to database
  - Configured workflow to run on port 5000

## Project Structure
- `backend/` - Main application code
  - `main.py` - FastAPI app entry point
  - `models.py` - Database models
  - `blockchain.py` - Blockchain implementation
  - `face_utils.py` - Face detection utilities
  - `routes/` - API route handlers
  - `templates/` - HTML templates
  - `static/` - CSS and JavaScript files

## How to Run
The application runs automatically via the configured workflow on port 5000.
To run manually: `uvicorn backend.main:app --host 0.0.0.0 --port 5000 --reload`

## Features Implemented
### Voter Features
✅ Voter registration with face capture
✅ Face verification using OpenCV before voting
✅ Blockchain for tamper-proof vote storage
✅ Voting system with duplicate prevention
✅ Responsive web interface

### Admin Features
✅ JWT-based authentication with secure login
✅ 3D blockchain visualization with rotating blocks
✅ Real-time statistics dashboard
✅ Full CRUD operations for elections
✅ Full CRUD operations for candidates
✅ Full CRUD operations for voters
✅ Interactive charts for voting results
✅ Blockchain ledger explorer
✅ Modern glassmorphism UI with dark theme

## API Endpoints
### Public Endpoints
- GET / - Home page
- GET /register - Voter registration page
- GET /vote - Voting page
- POST /api/register - Register voter
- POST /api/verify-face - Verify face
- POST /api/vote - Cast vote
- GET /api/candidates - Get candidates

### Admin Endpoints (JWT Protected)
- GET /admin/login - Admin login page
- GET /admin - Admin dashboard (3D)
- POST /api/auth/login - Admin authentication
- GET /api/admin/stats - Dashboard statistics
- GET /api/admin/elections - List all elections
- POST /api/admin/elections - Create new election
- DELETE /api/admin/elections/{id} - Delete election
- GET /api/admin/candidates - List all candidates
- POST /api/admin/candidates - Add new candidate
- DELETE /api/admin/candidates/{id} - Delete candidate
- GET /api/admin/voters - List all voters
- DELETE /api/admin/voters/{id} - Delete voter
- GET /api/admin/blockchain - View blockchain ledger
- GET /api/admin/results - Get detailed voting results

## Database
SQLite database stored at `backend/voting_system.db`
- Voters table: stores voter info and face data
- Candidates table: stores candidate information
- Blockchain is stored in memory (could be persisted if needed)

## Admin Credentials
- **Username**: admin
- **Password**: admin123
- ⚠️ **For Production Deployment**:
  - Change the default password and regenerate the pbkdf2_sha256 hash
  - Move `SECRET_KEY` from auth.py to environment variables (use SESSION_SECRET)
  - Rotate the JWT secret key
  - Consider implementing password reset functionality
  - Add rate limiting to login endpoint

## Notes
- Face detection uses OpenCV Haar Cascade (simpler than face_recognition library, no dlib/cmake required)
- Blockchain validates on each view to ensure integrity
- System prevents duplicate voting with voter ID tracking
- Sample candidates are auto-created on startup
- JWT tokens expire after 60 minutes
- Password authentication uses pbkdf2_sha256 hashing (secure and production-ready)
- Tailwind CSS is loaded via CDN (suitable for university project, use PostCSS for production)
- 3D blockchain visualization uses Three.js with animated rotating blocks

## Design Choices
- **OpenCV over face_recognition**: Avoids complex dlib/cmake compilation issues
- **JWT over session cookies**: Stateless authentication, suitable for REST APIs
- **pbkdf2_sha256 over bcrypt**: Secure password hashing without bcrypt compatibility issues
- **SQLite over PostgreSQL**: Simpler setup for university project
- **Tailwind CDN over build process**: Rapid development without build configuration
- **Three.js for 3D**: Modern, impressive visualization for final year project presentation
- **Glassmorphism design**: Modern crypto/blockchain aesthetic with neon accents
