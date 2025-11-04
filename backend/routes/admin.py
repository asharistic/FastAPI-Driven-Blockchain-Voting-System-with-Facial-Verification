"""
API routes for admin dashboard and blockchain viewing
"""
from fastapi import APIRouter
from backend.blockchain import voting_blockchain
from backend import database as db

router = APIRouter(prefix="/api", tags=["admin"])


@router.get("/chain")
async def get_blockchain():
    """
    Get the entire blockchain
    """
    return {
        "length": len(voting_blockchain.chain),
        "chain": voting_blockchain.get_chain(),
        "is_valid": voting_blockchain.is_chain_valid()
    }


@router.get("/results")
async def get_results():
    """
    Get voting results (total votes per candidate)
    """
    # Get vote counts from blockchain
    vote_counts = voting_blockchain.get_votes_by_candidate()
    
    # Get candidate details
    candidates = db.list_candidates()
    
    results = []
    for candidate in candidates:
        results.append({
            "candidate_id": candidate["candidate_id"],
            "name": candidate["name"],
            "party": candidate.get("party"),
            "votes": vote_counts.get(candidate["candidate_id"], 0)
        })
    
    # Sort by votes (descending)
    results.sort(key=lambda x: x["votes"], reverse=True)
    
    total_votes = sum(r["votes"] for r in results)
    
    return {
        "total_votes": total_votes,
        "results": results
    }
