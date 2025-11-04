"""
API routes for voting functionality
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from backend import database as db
from backend.blockchain import voting_blockchain
from backend.face_utils import base64_to_image, check_duplicate_face
from datetime import datetime

router = APIRouter(prefix="/api", tags=["votes"])


class VoteSubmission(BaseModel):
    voter_id: str
    candidate_id: str
    face_image: str  # Base64 encoded image for duplicate face verification


@router.post("/vote")
async def cast_vote(vote_data: VoteSubmission):
    """
    Cast a vote for a candidate (adds to blockchain)
    """
    # Verify voter exists
    voter = db.get_voter_by_voter_id(vote_data.voter_id)
    if not voter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voter not found"
        )
    
    # Check if voter has already voted
    if voter["has_voted"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already voted"
        )
    
    # Verify candidate exists
    candidate = db.get_candidate_by_candidate_id(vote_data.candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    try:
        # Check for duplicate face - prevent same person voting with different voter_id
        if vote_data.face_image:
            image = base64_to_image(vote_data.face_image)
            # Get all voters who have already voted (to check for duplicate faces)
            all_voters = db.list_voters_with_faces()
            voted_voters = [v for v in all_voters if v["has_voted"] and v["voter_id"] != vote_data.voter_id]
            
            if voted_voters:
                duplicate_voter = check_duplicate_face(image, voted_voters)
                if duplicate_voter:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"This face has already voted with voter ID: {duplicate_voter['voter_id']} (Name: {duplicate_voter['name']}). Each person can only vote once."
                    )
        
        # Add vote to blockchain
        vote_block_data = {
            "voter_id": vote_data.voter_id,
            "candidate_id": vote_data.candidate_id,
            "candidate_name": candidate["name"],
            "timestamp": datetime.now().isoformat()
        }
        
        new_block = voting_blockchain.add_block(vote_block_data)
        
        # Mark voter as having voted
        db.set_voter_has_voted(vote_data.voter_id)
        
        return {
            "success": True,
            "message": f"Vote cast successfully for {candidate['name']}",
            "block_index": new_block.index,
            "block_hash": new_block.hash
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cast vote: {str(e)}"
        )


@router.get("/candidates")
async def get_all_candidates():
    """
    Get all candidates with their election information
    """
    candidates = db.list_candidates()
    elections = db.list_elections()
    
    # Create a mapping of election_id to election info
    election_map = {e["id"]: e for e in elections}
    
    candidate_list = []
    for candidate in candidates:
        election_id = candidate.get("election_id")
        election_info = election_map.get(election_id) if election_id else None
        
        candidate_list.append({
            "candidate_id": candidate["candidate_id"],
            "name": candidate["name"],
            "party": candidate.get("party"),
            "election_id": election_id,
            "election_title": election_info["title"] if election_info else None,
            "election_description": election_info.get("description") if election_info else None,
            "is_active": bool(election_info.get("is_active", 0)) if election_info else False
        })
    
    # Filter to only show candidates from active elections (or all if no active elections)
    active_elections = [e for e in elections if e.get("is_active")]
    if active_elections:
        active_election_ids = {e["id"] for e in active_elections}
        candidate_list = [c for c in candidate_list if c["election_id"] in active_election_ids]
    
    return {
        "total_candidates": len(candidate_list),
        "candidates": candidate_list
    }
