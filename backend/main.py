"""
FastAPI Blockchain Voting System with Facial Verification
Main application entry point
"""
from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend import database as db
from backend.routes import voters, votes, admin, auth, admin_enhanced

# Initialize FastAPI app
app = FastAPI(
    title="Blockchain Voting System",
    description="Secure voting system with facial verification and blockchain",
    version="2.0.0"
)

# Configure CORS to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (kept for potential future use)
# app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Setup templates (not used - React frontend handles UI)
# templates = Jinja2Templates(directory="backend/templates")

# Include routers
app.include_router(voters.router)
app.include_router(votes.router)
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(admin_enhanced.router)


# Initialize database and add sample data
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Initializing database...")
    init_db()
    
    # Add sample candidates if none exist
    try:
        existing_candidates = len(db.list_candidates())
        if existing_candidates == 0:
            sample_candidates = [
                {"candidate_id": "C001", "name": "Alice Johnson", "party": "Progressive Party"},
                {"candidate_id": "C002", "name": "Bob Smith", "party": "Democratic Alliance"},
                {"candidate_id": "C003", "name": "Carol Williams", "party": "Independent"},
                {"candidate_id": "C004", "name": "David Brown", "party": "Green Party"},
            ]
            for c in sample_candidates:
                db.create_candidate(c)
            print("Sample candidates added to database")
        else:
            print(f"Database already contains {existing_candidates} candidates")
    except Exception as e:
        print(f"Error initializing candidates: {str(e)}")


# Frontend routes (removed - React frontend handles all UI)
# All frontend routes are now handled by React Router on http://localhost:3000


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Blockchain Voting System",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
