"""
FastAPI Blockchain Voting System with Facial Verification
Main application entry point
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from backend.database import init_db, get_db
from backend.models import Candidate
from backend.routes import voters, votes, admin
from sqlalchemy.orm import Session

# Initialize FastAPI app
app = FastAPI(
    title="Blockchain Voting System",
    description="Secure voting system with facial verification and blockchain",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="backend/templates")

# Include routers
app.include_router(voters.router)
app.include_router(votes.router)
app.include_router(admin.router)


# Initialize database and add sample data
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Initializing database...")
    init_db()
    
    # Add sample candidates if none exist
    db = next(get_db())
    try:
        existing_candidates = db.query(Candidate).count()
        if existing_candidates == 0:
            sample_candidates = [
                Candidate(candidate_id="C001", name="Alice Johnson", party="Progressive Party"),
                Candidate(candidate_id="C002", name="Bob Smith", party="Democratic Alliance"),
                Candidate(candidate_id="C003", name="Carol Williams", party="Independent"),
                Candidate(candidate_id="C004", name="David Brown", party="Green Party"),
            ]
            db.add_all(sample_candidates)
            db.commit()
            print("Sample candidates added to database")
        else:
            print(f"Database already contains {existing_candidates} candidates")
    except Exception as e:
        print(f"Error initializing candidates: {str(e)}")
        db.rollback()
    finally:
        db.close()


# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Voter registration page"""
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/vote", response_class=HTMLResponse)
async def vote_page(request: Request):
    """Voting page"""
    return templates.TemplateResponse("vote.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Admin dashboard page"""
    return templates.TemplateResponse("admin.html", {"request": request})


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
