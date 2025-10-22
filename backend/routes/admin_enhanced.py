"""
Enhanced admin routes with CRUD operations and JWT authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from backend.database import get_db
from backend.blockchain import voting_blockchain
from backend.models import Candidate, Voter, Election
from backend.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


# Pydantic models for requests
class ElectionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime


class ElectionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool] = None


class CandidateCreate(BaseModel):
    candidate_id: str
    name: str
    party: Optional[str] = None
    election_id: Optional[int] = None
    image_url: Optional[str] = None
    bio: Optional[str] = None


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    party: Optional[str] = None
    election_id: Optional[int] = None
    image_url: Optional[str] = None
    bio: Optional[str] = None


class VoterUpdate(BaseModel):
    name: Optional[str] = None
    has_voted: Optional[bool] = None


# ========== ELECTION MANAGEMENT ==========

@router.post("/elections")
async def create_election(election: ElectionCreate, db: Session = Depends(get_db)):
    """Create a new election"""
    new_election = Election(**election.dict())
    db.add(new_election)
    db.commit()
    db.refresh(new_election)
    return {
        "success": True,
        "message": "Election created successfully",
        "election": {
            "id": new_election.id,
            "title": new_election.title,
            "description": new_election.description,
            "start_time": new_election.start_time.isoformat(),
            "end_time": new_election.end_time.isoformat(),
            "is_active": new_election.is_active
        }
    }


@router.get("/elections")
async def get_elections(db: Session = Depends(get_db)):
    """Get all elections"""
    elections = db.query(Election).all()
    return {
        "elections": [
            {
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat(),
                "is_active": e.is_active,
                "created_at": e.created_at.isoformat() if e.created_at else None
            }
            for e in elections
        ]
    }


@router.put("/elections/{election_id}")
async def update_election(election_id: int, election_data: ElectionUpdate, db: Session = Depends(get_db)):
    """Update an election"""
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    update_data = election_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(election, field, value)
    
    db.commit()
    db.refresh(election)
    return {"success": True, "message": "Election updated successfully"}


@router.delete("/elections/{election_id}")
async def delete_election(election_id: int, db: Session = Depends(get_db)):
    """Delete an election"""
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    db.delete(election)
    db.commit()
    return {"success": True, "message": "Election deleted successfully"}


# ========== CANDIDATE MANAGEMENT ==========

@router.post("/candidates")
async def create_candidate(candidate: CandidateCreate, db: Session = Depends(get_db)):
    """Create a new candidate"""
    # Check if candidate_id already exists
    existing = db.query(Candidate).filter(Candidate.candidate_id == candidate.candidate_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Candidate ID already exists")
    
    new_candidate = Candidate(**candidate.dict())
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    return {
        "success": True,
        "message": "Candidate created successfully",
        "candidate": {
            "id": new_candidate.id,
            "candidate_id": new_candidate.candidate_id,
            "name": new_candidate.name,
            "party": new_candidate.party
        }
    }


@router.get("/candidates")
async def get_all_candidates(db: Session = Depends(get_db)):
    """Get all candidates (admin view with all details)"""
    candidates = db.query(Candidate).all()
    return {
        "candidates": [
            {
                "id": c.id,
                "candidate_id": c.candidate_id,
                "name": c.name,
                "party": c.party,
                "election_id": c.election_id,
                "image_url": c.image_url,
                "bio": c.bio
            }
            for c in candidates
        ]
    }


@router.put("/candidates/{candidate_id}")
async def update_candidate(candidate_id: str, candidate_data: CandidateUpdate, db: Session = Depends(get_db)):
    """Update a candidate"""
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    update_data = candidate_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)
    
    db.commit()
    db.refresh(candidate)
    return {"success": True, "message": "Candidate updated successfully"}


@router.delete("/candidates/{candidate_id}")
async def delete_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """Delete a candidate"""
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    db.delete(candidate)
    db.commit()
    return {"success": True, "message": "Candidate deleted successfully"}


# ========== VOTER MANAGEMENT ==========

@router.get("/voters")
async def get_all_voters(db: Session = Depends(get_db)):
    """Get all voters with detailed information"""
    voters = db.query(Voter).all()
    return {
        "total_voters": len(voters),
        "voters": [
            {
                "id": v.id,
                "voter_id": v.voter_id,
                "name": v.name,
                "has_voted": v.has_voted,
                "has_face_data": v.face_data is not None,
                "registered_at": v.registered_at.isoformat() if v.registered_at else None
            }
            for v in voters
        ]
    }


@router.put("/voters/{voter_id}")
async def update_voter(voter_id: str, voter_data: VoterUpdate, db: Session = Depends(get_db)):
    """Update voter information"""
    voter = db.query(Voter).filter(Voter.voter_id == voter_id).first()
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    update_data = voter_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(voter, field, value)
    
    db.commit()
    db.refresh(voter)
    return {"success": True, "message": "Voter updated successfully"}


@router.delete("/voters/{voter_id}")
async def delete_voter(voter_id: str, db: Session = Depends(get_db)):
    """Delete a voter"""
    voter = db.query(Voter).filter(Voter.voter_id == voter_id).first()
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    db.delete(voter)
    db.commit()
    return {"success": True, "message": "Voter deleted successfully"}


# ========== BLOCKCHAIN & RESULTS ==========

@router.get("/blockchain")
async def get_blockchain():
    """Get the complete blockchain with validation status"""
    return {
        "length": len(voting_blockchain.chain),
        "chain": voting_blockchain.get_chain(),
        "is_valid": voting_blockchain.is_chain_valid()
    }


@router.get("/results")
async def get_voting_results(db: Session = Depends(get_db)):
    """Get detailed voting results"""
    vote_counts = voting_blockchain.get_votes_by_candidate()
    candidates = db.query(Candidate).all()
    
    results = []
    for candidate in candidates:
        votes = vote_counts.get(candidate.candidate_id, 0)
        results.append({
            "candidate_id": candidate.candidate_id,
            "name": candidate.name,
            "party": candidate.party,
            "votes": votes
        })
    
    results.sort(key=lambda x: x["votes"], reverse=True)
    total_votes = sum(r["votes"] for r in results)
    
    return {
        "total_votes": total_votes,
        "results": results
    }


# ========== STATISTICS ==========

@router.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get overall system statistics"""
    total_voters = db.query(Voter).count()
    voters_who_voted = db.query(Voter).filter(Voter.has_voted == True).count()
    total_candidates = db.query(Candidate).count()
    total_elections = db.query(Election).count()
    active_elections = db.query(Election).filter(Election.is_active == True).count()
    blockchain_blocks = len(voting_blockchain.chain)
    blockchain_valid = voting_blockchain.is_chain_valid()
    
    return {
        "total_voters": total_voters,
        "voters_who_voted": voters_who_voted,
        "voting_participation_rate": (voters_who_voted / total_voters * 100) if total_voters > 0 else 0,
        "total_candidates": total_candidates,
        "total_elections": total_elections,
        "active_elections": active_elections,
        "blockchain_blocks": blockchain_blocks,
        "blockchain_valid": blockchain_valid
    }
