"""
API routes for voter registration and verification
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.models import Voter
from backend.face_utils import base64_to_image, detect_face, save_face_data, compare_faces
import cv2

router = APIRouter(prefix="/api", tags=["voters"])


class VoterRegistration(BaseModel):
    voter_id: str
    name: str
    face_image: str  # Base64 encoded image


class FaceVerification(BaseModel):
    voter_id: str
    face_image: str  # Base64 encoded image


@router.post("/register")
async def register_voter(voter_data: VoterRegistration, db: Session = Depends(get_db)):
    """
    Register a new voter with face data
    """
    # Check if voter already exists
    existing_voter = db.query(Voter).filter(Voter.voter_id == voter_data.voter_id).first()
    if existing_voter:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voter ID already registered"
        )
    
    try:
        # Convert base64 to image
        image = base64_to_image(voter_data.face_image)
        
        # Check if face is detected
        if not detect_face(image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the image. Please ensure your face is clearly visible."
            )
        
        # Save face data
        face_bytes = save_face_data(image)
        
        # Create new voter
        new_voter = Voter(
            voter_id=voter_data.voter_id,
            name=voter_data.name,
            face_data=face_bytes
        )
        
        db.add(new_voter)
        db.commit()
        db.refresh(new_voter)
        
        return {
            "success": True,
            "message": f"Voter {voter_data.name} registered successfully",
            "voter_id": voter_data.voter_id
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/verify-face")
async def verify_face(verification_data: FaceVerification, db: Session = Depends(get_db)):
    """
    Verify voter's face before voting
    """
    # Find voter
    voter = db.query(Voter).filter(Voter.voter_id == verification_data.voter_id).first()
    
    if not voter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voter ID not found. Please register first."
        )
    
    # Check if voter has already voted
    if voter.has_voted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already voted. Each voter can only vote once."
        )
    
    try:
        # Convert base64 to image
        image = base64_to_image(verification_data.face_image)
        
        # Check if face is detected
        if not detect_face(image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected. Please ensure your face is clearly visible."
            )
        
        # Compare faces
        if not compare_faces(voter.face_data, image):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Face verification failed. Face does not match registered data."
            )
        
        return {
            "success": True,
            "message": "Face verified successfully",
            "voter_name": voter.name,
            "voter_id": voter.voter_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


@router.get("/voters")
async def get_all_voters(db: Session = Depends(get_db)):
    """
    Get all registered voters (admin function)
    """
    voters = db.query(Voter).all()
    return {
        "total_voters": len(voters),
        "voters": [
            {
                "voter_id": voter.voter_id,
                "name": voter.name,
                "has_voted": voter.has_voted,
                "registered_at": voter.registered_at.isoformat() if voter.registered_at else None
            }
            for voter in voters
        ]
    }
