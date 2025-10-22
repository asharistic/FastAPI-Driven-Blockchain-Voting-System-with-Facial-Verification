"""
API routes for voting functionality
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.models import Voter, Candidate
from backend.blockchain import voting_blockchain
from datetime import datetime

router = APIRouter(prefix="/api", tags=["votes"])


class VoteSubmission(BaseModel):
    voter_id: str
    candidate_id: str


@router.post("/vote")
async def cast_vote(vote_data: VoteSubmission, db: Session = Depends(get_db)):
    """
    Cast a vote for a candidate (adds to blockchain)
    """
    # Verify voter exists
    voter = db.query(Voter).filter(Voter.voter_id == vote_data.voter_id).first()
    if not voter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voter not found"
        )
    
    # Check if voter has already voted
    if voter.has_voted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already voted"
        )
    
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.candidate_id == vote_data.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    try:
        # Add vote to blockchain
        vote_block_data = {
            "voter_id": vote_data.voter_id,
            "candidate_id": vote_data.candidate_id,
            "candidate_name": candidate.name,
            "timestamp": datetime.now().isoformat()
        }
        
        new_block = voting_blockchain.add_block(vote_block_data)
        
        # Mark voter as having voted
        voter.has_voted = True
        db.commit()
        
        return {
            "success": True,
            "message": f"Vote cast successfully for {candidate.name}",
            "block_index": new_block.index,
            "block_hash": new_block.hash
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cast vote: {str(e)}"
        )


@router.get("/candidates")
async def get_all_candidates(db: Session = Depends(get_db)):
    """
    Get all candidates
    """
    candidates = db.query(Candidate).all()
    return {
        "total_candidates": len(candidates),
        "candidates": [
            {
                "candidate_id": candidate.candidate_id,
                "name": candidate.name,
                "party": candidate.party
            }
            for candidate in candidates
        ]
    }
