# Blockchain Voting System with Facial Verification

## Project Overview
A FastAPI-based blockchain voting system with facial verification for a university final year project. Features voter registration with face capture, facial verification before voting, secure vote storage in a custom blockchain, and an admin dashboard.

## Tech Stack
- **Backend**: FastAPI (Python 3.11)
- **Database**: SQLite with SQLAlchemy
- **Face Detection**: OpenCV with Haar Cascade
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Blockchain**: Custom Python implementation

## Recent Changes
- **2025-10-22**: Initial project setup
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
✅ Voter registration with face capture
✅ Face verification using OpenCV
✅ Blockchain for secure vote storage
✅ Voting system with duplicate prevention
✅ Admin dashboard with results and blockchain explorer
✅ RESTful API endpoints
✅ Responsive web interface

## API Endpoints
- POST /api/register - Register voter
- POST /api/verify-face - Verify face
- POST /api/vote - Cast vote
- GET /api/candidates - Get candidates
- GET /api/voters - Get voters
- GET /api/chain - View blockchain
- GET /api/results - Get results

## Database
SQLite database stored at `backend/voting_system.db`
- Voters table: stores voter info and face data
- Candidates table: stores candidate information
- Blockchain is stored in memory (could be persisted if needed)

## Notes
- Face detection uses OpenCV Haar Cascade (simpler than face_recognition library)
- Blockchain validates on each view to ensure integrity
- System prevents duplicate voting
- Sample candidates are auto-created on startup
