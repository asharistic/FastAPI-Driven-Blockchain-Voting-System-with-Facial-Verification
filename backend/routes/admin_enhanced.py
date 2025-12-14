"""
Enhanced admin routes with CRUD operations and JWT authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from backend import database as db
from backend.blockchain import voting_blockchain
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
async def create_election(election: ElectionCreate):
    """Create a new election"""
    new_id = db.create_election({
        "title": election.title,
        "description": election.description,
        "start_time": election.start_time.isoformat(),
        "end_time": election.end_time.isoformat(),
        "is_active": True,
    })
    return {
        "success": True,
        "message": "Election created successfully",
        "election": {
            "id": new_id,
            "title": election.title,
            "description": election.description,
            "start_time": election.start_time.isoformat(),
            "end_time": election.end_time.isoformat(),
            "is_active": True
        }
    }


@router.get("/elections")
async def get_elections():
    """Get all elections"""
    elections = db.list_elections()
    return {
        "elections": [
            {
                "id": e["id"],
                "title": e["title"],
                "description": e.get("description"),
                "start_time": e.get("start_time"),
                "end_time": e.get("end_time"),
                "is_active": bool(e.get("is_active", False)),
                "created_at": e.get("created_at")
            }
            for e in elections
        ]
    }


@router.put("/elections/{election_id}")
async def update_election(election_id: int, election_data: ElectionUpdate):
    """Update an election"""
    election = db.get_election_by_id(election_id)
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    update_data = election_data.dict(exclude_unset=True)
    # Normalize booleans and datetimes to stored format
    if "start_time" in update_data and isinstance(update_data["start_time"], datetime):
        update_data["start_time"] = update_data["start_time"].isoformat()
    if "end_time" in update_data and isinstance(update_data["end_time"], datetime):
        update_data["end_time"] = update_data["end_time"].isoformat()
    if "is_active" in update_data:
        update_data["is_active"] = bool(update_data["is_active"])
    db.update_election(election_id, update_data)
    return {"success": True, "message": "Election updated successfully"}


@router.delete("/elections/{election_id}")
async def delete_election(election_id: int):
    """Delete an election and all associated candidates"""
    election = db.get_election_by_id(election_id)
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    # Get all candidates associated with this election
    all_candidates = db.list_candidates()
    candidates_to_delete = [c["candidate_id"] for c in all_candidates if c.get("election_id") == election_id]
    
    # Delete all associated candidates
    deleted_candidates_count = 0
    for candidate_id in candidates_to_delete:
        if db.delete_candidate(candidate_id):
            deleted_candidates_count += 1
    
    # Delete the election
    db.delete_election(election_id)
    
    message = f"Election deleted successfully"
    if deleted_candidates_count > 0:
        message += f". {deleted_candidates_count} candidate(s) also deleted."
    
    return {"success": True, "message": message, "deleted_candidates": deleted_candidates_count}


# ========== CANDIDATE MANAGEMENT ==========

@router.post("/candidates")
async def create_candidate(candidate: CandidateCreate):
    """Create a new candidate"""
    # Check if candidate_id already exists
    existing = db.get_candidate_by_candidate_id(candidate.candidate_id)
    if existing:
        raise HTTPException(status_code=400, detail="Candidate ID already exists")
    
    # Validate that an election exists
    elections = db.list_elections()
    if not elections:
        raise HTTPException(
            status_code=400, 
            detail="Cannot create candidates without an election. Please create an election first."
        )
    
    # If election_id is provided, validate it exists
    if candidate.election_id:
        election_exists = any(e["id"] == candidate.election_id for e in elections)
        if not election_exists:
            raise HTTPException(
                status_code=404,
                detail=f"Election with ID {candidate.election_id} not found"
            )
    else:
        # If no election_id provided, use the first active election, or first election if none active
        active_elections = [e for e in elections if e.get("is_active")]
        if active_elections:
            candidate.election_id = active_elections[0]["id"]
        else:
            # Use the first available election
            candidate.election_id = elections[0]["id"]
    
    db.create_candidate(candidate.dict())
    return {
        "success": True,
        "message": "Candidate created successfully",
        "candidate": {
            "candidate_id": candidate.candidate_id,
            "name": candidate.name,
            "party": candidate.party,
            "election_id": candidate.election_id
        }
    }


@router.get("/candidates")
async def get_all_candidates():
    """Get all candidates (admin view with all details)"""
    candidates = db.list_candidates()
    return {
        "candidates": [
            {
                "candidate_id": c["candidate_id"],
                "name": c["name"],
                "party": c.get("party"),
                "election_id": c.get("election_id"),
                "image_url": c.get("image_url"),
                "bio": c.get("bio")
            }
            for c in candidates
        ]
    }


@router.put("/candidates/{candidate_id}")
async def update_candidate(candidate_id: str, candidate_data: CandidateUpdate):
    """Update a candidate"""
    candidate = db.get_candidate_by_candidate_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    update_data = candidate_data.dict(exclude_unset=True)
    db.update_candidate(candidate_id, update_data)
    return {"success": True, "message": "Candidate updated successfully"}


@router.delete("/candidates/{candidate_id}")
async def delete_candidate(candidate_id: str):
    """Delete a candidate"""
    candidate = db.get_candidate_by_candidate_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    db.delete_candidate(candidate_id)
    return {"success": True, "message": "Candidate deleted successfully"}


# ========== VOTER MANAGEMENT ==========

@router.get("/voters")
async def get_all_voters():
    """Get all voters with detailed information"""
    voters = db.list_voters()
    return {
        "total_voters": len(voters),
        "voters": [
            {
                "voter_id": v["voter_id"],
                "name": v["name"],
                "has_voted": bool(v["has_voted"]),
                "has_face_data": True,
                "registered_at": v.get("registered_at")
            }
            for v in voters
        ]
    }


@router.put("/voters/{voter_id}")
async def update_voter(voter_id: str, voter_data: VoterUpdate):
    """Update voter information"""
    voter = db.get_voter_by_voter_id(voter_id)
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    update_data = voter_data.dict(exclude_unset=True)
    db.update_voter(voter_id, update_data)
    return {"success": True, "message": "Voter updated successfully"}


@router.delete("/voters/{voter_id}")
async def delete_voter(voter_id: str):
    """Delete a voter"""
    voter = db.get_voter_by_voter_id(voter_id)
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    db.delete_voter(voter_id)
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
async def get_voting_results():
    """Get detailed voting results"""
    vote_counts = voting_blockchain.get_votes_by_candidate()
    candidates = db.list_candidates()
    
    results = []
    for candidate in candidates:
        votes = vote_counts.get(candidate["candidate_id"], 0)
        results.append({
            "candidate_id": candidate["candidate_id"],
            "name": candidate["name"],
            "party": candidate.get("party"),
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
async def get_statistics():
    """Get overall system statistics"""
    total_voters = db.count("voters")
    # Count voters who voted
    all_voters = db.list_voters()
    voters_who_voted = sum(1 for v in all_voters if v.get("has_voted", False))
    total_candidates = db.count("candidates")
    total_elections = db.count("elections")
    # Count active elections
    all_elections = db.list_elections()
    active_elections = sum(1 for e in all_elections if e.get("is_active", False))
    blockchain_blocks = len(voting_blockchain.chain)
    blockchain_valid = voting_blockchain.is_chain_valid()
    
    # Calculate total votes from blockchain (excluding genesis block)
    vote_counts = voting_blockchain.get_votes_by_candidate()
    total_votes = sum(vote_counts.values())
    
    return {
        "total_voters": total_voters,
        "voters_who_voted": voters_who_voted,
        "voting_participation_rate": (voters_who_voted / total_voters * 100) if total_voters > 0 else 0,
        "total_candidates": total_candidates,
        "total_elections": total_elections,
        "active_elections": active_elections,
        "blockchain_blocks": blockchain_blocks,
        "blockchain_valid": blockchain_valid,
        "total_votes": total_votes
    }
