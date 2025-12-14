"""
API routes for voter registration and verification using DeepFace
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from backend import database as db
from backend.face_utils import (
    base64_to_image, 
    detect_face, 
    generate_face_embedding, 
    verify_face_with_embedding, 
    check_duplicate_face,
    get_verification_threshold,
    set_verification_threshold
)

router = APIRouter(prefix="/api", tags=["voters"])


class VoterRegistration(BaseModel):
    voter_id: str
    name: str
    face_image: str  # Base64 encoded image


class FaceVerification(BaseModel):
    voter_id: str
    face_image: str  # Base64 encoded image


@router.post("/register")
async def register_voter(voter_data: VoterRegistration):
    """
    Register a new voter with face embedding using DeepFace (FaceNet)
    
    Process:
    1. Check if voter ID already exists
    2. Convert base64 image to numpy array
    3. Detect face in image
    4. Check for duplicate face (prevent same person registering twice)
    5. Generate face embedding using DeepFace FaceNet model
    6. Store embedding in PostgreSQL database
    
    Returns:
        Success message with voter ID
    """
    # Check if voter ID already exists
    existing_voter = db.get_voter_by_voter_id(voter_data.voter_id)
    if existing_voter:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voter ID already registered"
        )
    
    try:
        print(f"[REGISTRATION] Starting registration for voter_id: {voter_data.voter_id}, name: {voter_data.name}")
        print(f"[REGISTRATION] Face image length: {len(voter_data.face_image)} characters")
        
        # Convert base64 to image
        print("[REGISTRATION] Step 1: Converting base64 to image...")
        image = base64_to_image(voter_data.face_image)
        print(f"[REGISTRATION] Image converted successfully. Shape: {image.shape}")
        
        # Check if face is detected using DeepFace
        print("[REGISTRATION] Step 2: Detecting face with DeepFace...")
        face_detected = detect_face(image)
        print(f"[REGISTRATION] Face detection result: {face_detected}")
        
        if not face_detected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the image. Please ensure your face is clearly visible and facing the camera."
            )
        
        # Check for duplicate face (prevent same person registering with different ID/name)
        # This enforces one-person-one-registration rule
        print("[REGISTRATION] Step 3: Checking for duplicate faces...")
        existing_voters = db.list_voters_with_faces()
        print(f"[REGISTRATION] Found {len(existing_voters)} existing voters with embeddings")
        
        duplicate_voter = check_duplicate_face(image, existing_voters)
        
        if duplicate_voter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"This face is already registered with voter ID: {duplicate_voter['voter_id']} (Name: {duplicate_voter['name']}). Each person can only register once."
            )
        
        # Generate face embedding using DeepFace FaceNet model
        # This creates a 128-dimensional vector representing the face
        print("[REGISTRATION] Step 4: Generating face embedding with DeepFace FaceNet...")
        print("[REGISTRATION] This may take 10-30 seconds on first use (downloading model)...")
        face_embedding = generate_face_embedding(image)
        print(f"[REGISTRATION] Embedding generated successfully. Dimensions: {len(face_embedding)}")
        
        # Create new voter with face embedding
        print("[REGISTRATION] Step 5: Saving to database...")
        db.create_voter(voter_data.voter_id, voter_data.name, face_embedding)
        print(f"[REGISTRATION] Voter {voter_data.voter_id} registered successfully!")
        
        return {
            "success": True,
            "message": f"Voter {voter_data.name} registered successfully with face embedding",
            "voter_id": voter_data.voter_id,
            "embedding_dimensions": len(face_embedding)
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        # Log the error for debugging
        print(f"[REGISTRATION ERROR] ValueError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_trace = traceback.format_exc()
        print(f"[REGISTRATION ERROR] Exception: {str(e)}")
        print(f"[REGISTRATION ERROR] Traceback:\n{error_trace}")
        
        # Provide more specific error messages
        error_msg = str(e)
        if "Face could not be detected" in error_msg or "No face detected" in error_msg:
            detail = "No face detected in the image. Please ensure your face is clearly visible and facing the camera."
        elif "embedding" in error_msg.lower():
            detail = "Failed to generate face embedding. Please try again with a clearer image."
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            detail = "Connection error. Please check your internet connection and try again."
        else:
            detail = f"Registration failed: {error_msg}"
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.post("/verify-face")
async def verify_face(verification_data: FaceVerification):
    """
    Verify voter's face before voting using DeepFace embedding comparison
    
    Process:
    1. Find voter by voter_id
    2. Check if voter has already voted
    3. Convert base64 image to numpy array
    4. Detect face in image
    5. Compare live face embedding with stored embedding
    6. Return verification result
    
    Returns:
        Success message if face matches, error if mismatch
    """
    # Find voter
    voter = db.get_voter_by_voter_id(verification_data.voter_id)
    
    if not voter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voter ID not found. Please register first."
        )
    
    # Check if voter has already voted
    if voter["has_voted"]:
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
                detail="No face detected in the image. Please ensure your face is clearly visible and facing the camera."
            )
        
        # Get stored embedding from database
        stored_embedding = voter.get("face_embedding")
        
        if not stored_embedding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face embedding found for this voter. Please re-register."
            )
        
        # Handle JSONB from PostgreSQL (might be dict or list)
        import json
        if isinstance(stored_embedding, dict):
            stored_embedding = stored_embedding.get("embedding", stored_embedding)
        elif isinstance(stored_embedding, str):
            stored_embedding = json.loads(stored_embedding)
        
        # Verify face using embedding comparison
        is_match, distance = verify_face_with_embedding(image, stored_embedding)
        
        if not is_match:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Face verification failed. Face does not match registered data. Distance: {distance:.4f} (threshold: {get_verification_threshold()})"
            )
        
        return {
            "success": True,
            "message": "Face verified successfully",
            "voter_name": voter["name"],
            "voter_id": voter["voter_id"],
            "distance": distance,
            "threshold": get_verification_threshold()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


@router.get("/voters")
async def get_all_voters():
    """
    Get all registered voters (admin function)
    """
    voters = db.list_voters()
    return {
        "total_voters": len(voters),
        "voters": [
            {
                "voter_id": voter["voter_id"],
                "name": voter["name"],
                "has_voted": bool(voter["has_voted"]),
                "registered_at": voter.get("registered_at"),
                "has_embedding": voter.get("face_embedding") is not None
            }
            for voter in voters
        ]
    }


class ThresholdConfig(BaseModel):
    threshold: float  # Face verification threshold (0.0 to 1.0)


@router.post("/config/threshold")
async def set_face_threshold(config: ThresholdConfig):
    """
    Configure face verification threshold (admin function)
    
    Threshold values:
    - Lower threshold (e.g., 0.3) = Stricter matching (fewer false positives)
    - Higher threshold (e.g., 0.5) = More lenient matching (more false positives)
    - Recommended: 0.3-0.5 for FaceNet model
    
    Args:
        threshold: Distance threshold (0.0 to 1.0)
    """
    try:
        set_verification_threshold(config.threshold)
        return {
            "success": True,
            "message": f"Face verification threshold set to {config.threshold}",
            "threshold": get_verification_threshold()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/config/threshold")
async def get_face_threshold():
    """
    Get current face verification threshold
    """
    return {
        "threshold": get_verification_threshold(),
        "description": "Distance threshold for face matching. Lower = stricter matching."
    }
