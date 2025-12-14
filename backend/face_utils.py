"""
Face detection and verification utilities using DeepFace (FaceNet model)
Replaces Haar Cascade with deep learning-based face recognition
"""
import os
# Set environment variables before importing TensorFlow/Keras
# This helps with compatibility issues between TensorFlow 2.20.0 and Keras 3.12.0
os.environ['TF_USE_LEGACY_KERAS'] = '1'
os.environ['TF_KERAS'] = '1'

import numpy as np
import base64
import json
from io import BytesIO
from PIL import Image
from deepface import DeepFace
from typing import List, Dict, Optional, Tuple

# Configuration: Face verification threshold
# Lower threshold = stricter matching (default: 0.4 for FaceNet)
# Distance metric: cosine distance (0 = identical, 1 = completely different)
FACE_VERIFICATION_THRESHOLD = 0.4

# DeepFace model configuration
# Using FaceNet model for face recognition
MODEL_NAME = "Facenet"
DETECTOR_BACKEND = "opencv"  # Can also use "mtcnn", "retinaface" for better accuracy


def base64_to_image(base64_string: str) -> np.ndarray:
    """
    Convert base64 string to numpy array image
    
    Args:
        base64_string: Base64 encoded image string (with or without data URL prefix)
    
    Returns:
        numpy.ndarray: Image as numpy array in RGB format
    
    Raises:
        ValueError: If image cannot be decoded
    """
    try:
        # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,...")
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to bytes
        img_data = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        pil_image = Image.open(BytesIO(img_data))
        
        # Convert to RGB if necessary (handles RGBA, L, etc.)
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to numpy array
        image_array = np.array(pil_image)
        
        return image_array
        
    except Exception as e:
        raise ValueError(f"Error converting base64 to image: {str(e)}")


def detect_face(image: np.ndarray) -> bool:
    """
    Detect if a face is present in the image using DeepFace
    
    Args:
        image: numpy array image in RGB format
    
    Returns:
        bool: True if at least one face is detected, False otherwise
    
    Raises:
        ValueError: If image processing fails
    """
    try:
        # DeepFace automatically detects faces
        # If no face is found, it raises an exception
        result = DeepFace.extract_faces(
            img_path=image,  # DeepFace uses img_path parameter, accepts numpy array
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True  # Raises exception if no face found
        )
        
        # If we get here, at least one face was detected
        return len(result) > 0
        
    except ValueError as e:
        # No face detected
        if "Face could not be detected" in str(e) or "No face detected" in str(e):
                        return False
        raise
    except Exception as e:
        raise ValueError(f"Error detecting face: {str(e)}")


def generate_face_embedding(image: np.ndarray) -> List[float]:
    """
    Generate face embedding vector using DeepFace (FaceNet model)
    
    This function:
    1. Detects face in the image
    2. Extracts face region
    3. Generates 128-dimensional embedding vector using FaceNet
    
    Args:
        image: numpy array image in RGB format
    
    Returns:
        List[float]: Face embedding vector (128 dimensions for FaceNet)
    
    Raises:
        ValueError: If no face is detected or embedding generation fails
    """
    try:
        print(f"[DEEPFACE] Generating embedding with model: {MODEL_NAME}, detector: {DETECTOR_BACKEND}")
        print(f"[DEEPFACE] Image shape: {image.shape}, dtype: {image.dtype}")
        
        # DeepFace automatically handles face detection and embedding generation
        # model_name="Facenet" uses FaceNet architecture
        # Note: First call will download the model (~90MB) which may take 1-2 minutes
        embedding = DeepFace.represent(
            img_path=image,  # DeepFace accepts numpy array directly
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True,  # Raises exception if no face found
            align=True  # Align face for better accuracy
        )
        
        print(f"[DEEPFACE] Embedding generated. Result type: {type(embedding)}, Length: {len(embedding) if embedding else 0}")
        
        # DeepFace returns a list of dictionaries (one per detected face)
        # We take the first face's embedding
        if not embedding or len(embedding) == 0:
            raise ValueError("No face embedding could be generated")
        
        # Extract the embedding vector (128 dimensions for FaceNet)
        embedding_vector = embedding[0]["embedding"]
        
        # Convert numpy array to list for JSON serialization
        if isinstance(embedding_vector, np.ndarray):
            embedding_vector = embedding_vector.tolist()
        
        return embedding_vector
        
    except ValueError as e:
        # Re-raise with clearer message
        error_msg = str(e)
        if "Face could not be detected" in error_msg or "No face detected" in error_msg:
            raise ValueError("No face detected in the image. Please ensure your face is clearly visible and facing the camera.")
        raise ValueError(f"Error generating face embedding: {error_msg}")
    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_trace = traceback.format_exc()
        error_msg = str(e)
        print(f"[DEEPFACE ERROR] Exception in generate_face_embedding: {error_msg}")
        print(f"[DEEPFACE ERROR] Traceback:\n{error_trace}")
        
        # Provide clearer error messages
        if "Face could not be detected" in error_msg or "No face detected" in error_msg:
            raise ValueError("No face detected in the image. Please ensure your face is clearly visible and facing the camera.")
        elif "model" in error_msg.lower() or "download" in error_msg.lower():
            raise ValueError("Face recognition model is loading. Please wait a moment and try again.")
        else:
            raise ValueError(f"Error generating face embedding: {error_msg}")


def compare_face_embeddings(embedding1: List[float], embedding2: List[float], threshold: float = FACE_VERIFICATION_THRESHOLD) -> Tuple[bool, float]:
    """
    Compare two face embeddings using cosine distance
    
    Args:
        embedding1: First face embedding vector
        embedding2: Second face embedding vector
        threshold: Distance threshold for matching (default: 0.4)
                   Lower = stricter matching
    
    Returns:
        tuple[bool, float]: (is_match, distance)
        - is_match: True if embeddings match (distance <= threshold)
        - distance: Cosine distance between embeddings (0 = identical, 1 = completely different)
    """
    try:
        # Convert to numpy arrays for computation
        emb1 = np.array(embedding1, dtype=np.float32)
        emb2 = np.array(embedding2, dtype=np.float32)
        
        # Ensure same length
        if len(emb1) != len(emb2):
            raise ValueError(f"Embedding dimensions mismatch: {len(emb1)} vs {len(emb2)}")
        
        # Normalize vectors (L2 normalization)
        emb1_norm = emb1 / (np.linalg.norm(emb1) + 1e-10)
        emb2_norm = emb2 / (np.linalg.norm(emb2) + 1e-10)
        
        # Calculate cosine similarity (dot product of normalized vectors)
        cosine_similarity = np.dot(emb1_norm, emb2_norm)
        
        # Convert similarity to distance (distance = 1 - similarity)
        cosine_distance = 1.0 - cosine_similarity
        
        # Check if distance is below threshold (lower distance = more similar)
        is_match = cosine_distance <= threshold
        
        return is_match, float(cosine_distance)
        
    except Exception as e:
        raise ValueError(f"Error comparing embeddings: {str(e)}")


def verify_face_with_embedding(live_image: np.ndarray, stored_embedding: List[float], threshold: float = FACE_VERIFICATION_THRESHOLD) -> Tuple[bool, float]:
    """
    Verify a live face image against a stored embedding
    
    This function:
    1. Generates embedding from live image
    2. Compares with stored embedding
    3. Returns match result and distance
    
    Args:
        live_image: numpy array of live face image
        stored_embedding: Stored face embedding vector from database
        threshold: Distance threshold for matching
    
    Returns:
        tuple[bool, float]: (is_match, distance)
    """
    try:
        # Generate embedding from live image
        live_embedding = generate_face_embedding(live_image)
        
        # Compare embeddings
        is_match, distance = compare_face_embeddings(live_embedding, stored_embedding, threshold)
        
        return is_match, distance
        
    except Exception as e:
        raise ValueError(f"Error verifying face: {str(e)}")


def check_duplicate_face(new_face_image: np.ndarray, existing_voters: List[Dict], threshold: float = FACE_VERIFICATION_THRESHOLD) -> Optional[Dict]:
    """
    Check if a new face matches any existing registered voter
    
    This enforces one-person-one-vote by preventing the same person
    from registering multiple times with different voter IDs
    
    Args:
        new_face_image: numpy array of new face image
        existing_voters: List of existing voter dictionaries with face_embedding
        threshold: Distance threshold for matching
    
    Returns:
        Optional[Dict]: Matching voter dictionary if found, None otherwise
    """
    try:
        # Generate embedding for new face
        new_embedding = generate_face_embedding(new_face_image)
        
        # Compare with all existing voters
        for voter in existing_voters:
            stored_embedding = voter.get("face_embedding")
            
            # Skip if no embedding stored
            if not stored_embedding:
                continue
                
            # Handle JSONB from PostgreSQL (might be dict or list)
            if isinstance(stored_embedding, dict):
                # If stored as JSON object, extract the array
                stored_embedding = stored_embedding.get("embedding", stored_embedding)
            elif isinstance(stored_embedding, str):
                # If stored as JSON string, parse it
                stored_embedding = json.loads(stored_embedding)
            
            try:
                # Compare embeddings
                is_match, distance = compare_face_embeddings(new_embedding, stored_embedding, threshold)
                
                if is_match:
                    # Found a match - same person already registered
                    return voter
                    
            except Exception as e:
                # Skip this voter if comparison fails
                print(f"Error comparing with voter {voter.get('voter_id')}: {str(e)}")
                continue
        
        # No match found
        return None
        
    except Exception as e:
        raise ValueError(f"Error checking for duplicate face: {str(e)}")


def get_verification_threshold() -> float:
    """
    Get the current face verification threshold
    
    Returns:
        float: Current threshold value
    """
    return FACE_VERIFICATION_THRESHOLD


def set_verification_threshold(threshold: float) -> None:
    """
    Set the face verification threshold
    
    Args:
        threshold: New threshold value (0.0 to 1.0)
                  Lower = stricter matching
                  Recommended: 0.3-0.5 for FaceNet
    """
    global FACE_VERIFICATION_THRESHOLD
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("Threshold must be between 0.0 and 1.0")
    FACE_VERIFICATION_THRESHOLD = threshold
