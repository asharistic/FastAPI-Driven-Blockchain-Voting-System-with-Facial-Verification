"""
API routes for voting functionality with DeepFace face verification
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from backend import database as db
from backend.blockchain import voting_blockchain
from backend.face_utils import base64_to_image, detect_face, verify_face_with_embedding, check_duplicate_face, get_verification_threshold
from datetime import datetime
import json

router = APIRouter(prefix="/api", tags=["votes"])


class VoteSubmission(BaseModel):
    voter_id: str
    candidate_id: str
    face_image: str  # Base64 encoded image for face verification


@router.post("/vote")
async def cast_vote(vote_data: VoteSubmission):
    """
    Cast a vote for a candidate with DeepFace face verification
    
    This endpoint enforces one-person-one-vote by:
    1. Verifying the face matches the registered voter
    2. Checking if voter has already voted
    3. Checking for duplicate faces (prevent same person voting with different ID)
    4. Recording vote on blockchain
    5. Marking voter as voted
    
    Process:
    1. Verify voter exists
    2. Check if voter has already voted
    3. Verify candidate exists
    4. Detect face in submitted image
    5. Verify face matches registered voter's embedding
    6. Check for duplicate face (compare with all voters who have voted)
    7. Add vote to blockchain
    8. Mark voter as has_voted=True
    
    Returns:
        Success message with block information
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
            detail="You have already voted. Each voter can only vote once."
        )
    
    # Verify candidate exists
    candidate = db.get_candidate_by_candidate_id(vote_data.candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    try:
        # Convert base64 to image
        image = base64_to_image(vote_data.face_image)
        
        # Check if face is detected
        if not detect_face(image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the image. Please ensure your face is clearly visible and facing the camera."
            )
        
        # Verify face matches registered voter's embedding
        stored_embedding = voter.get("face_embedding")
        if not stored_embedding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face embedding found for this voter. Please re-register."
            )
        
        # Handle JSONB from PostgreSQL
        if isinstance(stored_embedding, dict):
            stored_embedding = stored_embedding.get("embedding", stored_embedding)
        elif isinstance(stored_embedding, str):
            stored_embedding = json.loads(stored_embedding)
        
        # Verify face matches registered voter
        is_match, distance = verify_face_with_embedding(image, stored_embedding)
        
        if not is_match:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Face verification failed. Face does not match registered voter. Distance: {distance:.4f} (threshold: {get_verification_threshold()})"
            )
        
        # Check for duplicate face - prevent same person voting with different voter_id
        # This enforces one-person-one-vote rule strictly
        all_voters = db.list_voters_with_faces()
        # Get all voters who have already voted (excluding current voter)
        voted_voters = [v for v in all_voters if v.get("has_voted") and v["voter_id"] != vote_data.voter_id]
        
        if voted_voters:
            duplicate_voter = check_duplicate_face(image, voted_voters)
            if duplicate_voter:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"This face has already voted with voter ID: {duplicate_voter['voter_id']} (Name: {duplicate_voter['name']}). Each person can only vote once."
                )
        
        # All checks passed - proceed with voting
        
        # Add vote to blockchain
        vote_block_data = {
            "voter_id": vote_data.voter_id,
            "candidate_id": vote_data.candidate_id,
            "candidate_name": candidate["name"],
            "timestamp": datetime.now().isoformat()
        }
        
        new_block = voting_blockchain.add_block(vote_block_data)
        
        # Mark voter as having voted (enforces one-person-one-vote)
        db.set_voter_has_voted(vote_data.voter_id)
        
        return {
            "success": True,
            "message": f"Vote cast successfully for {candidate['name']}",
            "block_index": new_block.index,
            "block_hash": new_block.hash,
            "face_verification": {
                "verified": True,
                "distance": distance,
                "threshold": get_verification_threshold()
            }
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
            "is_active": bool(election_info.get("is_active", False)) if election_info else False
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
