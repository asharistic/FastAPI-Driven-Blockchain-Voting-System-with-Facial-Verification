"""
Face detection and verification utilities using OpenCV
"""
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# Additional cascade for profile face detection (to reject profile faces)
# Try to load profile cascade, but continue if not available
try:
    profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
    PROFILE_CASCADE_AVAILABLE = profile_cascade.empty() == False
except:
    PROFILE_CASCADE_AVAILABLE = False
    profile_cascade = None

def base64_to_image(base64_string: str) -> np.ndarray:
    """Convert base64 string to OpenCV image"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to bytes
        img_data = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        pil_image = Image.open(BytesIO(img_data))
        
        # Convert to OpenCV format (BGR)
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return opencv_image
    except Exception as e:
        raise ValueError(f"Error converting base64 to image: {str(e)}")


def validate_frontal_face(image: np.ndarray, face_rect: tuple) -> bool:
    """
    Validate that the detected face is frontal (not profile/side view)
    Returns True if face appears to be frontal
    """
    (x, y, w, h) = face_rect
    img_height, img_width = image.shape[:2]
    
    # 1. Check aspect ratio - frontal faces should be roughly square (width/height between 0.7 and 1.3)
    aspect_ratio = w / h
    if aspect_ratio < 0.7 or aspect_ratio > 1.3:
        return False
    
    # 2. Check face size relative to image - should be reasonably sized (not too small)
    face_area = w * h
    image_area = img_width * img_height
    face_ratio = face_area / image_area
    if face_ratio < 0.05:  # Face should be at least 5% of image
        return False
    
    # 3. Check face position - should be reasonably centered (not too far to edges)
    center_x = x + w / 2
    center_y = y + h / 2
    margin_x = img_width * 0.15  # 15% margin from edges
    margin_y = img_height * 0.15
    
    if center_x < margin_x or center_x > (img_width - margin_x):
        return False
    if center_y < margin_y or center_y > (img_height - margin_y):
        return False
    
    # Convert to grayscale for detection checks
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 4. Check for profile face - if profile cascade detects the face, reject it
    if PROFILE_CASCADE_AVAILABLE and profile_cascade is not None:
        # Expand search region slightly around detected face
        expanded_x = max(0, x - w // 4)
        expanded_y = max(0, y - h // 4)
        expanded_w = min(img_width - expanded_x, w + w // 2)
        expanded_h = min(img_height - expanded_y, h + h // 2)
        
        roi = gray[expanded_y:expanded_y+expanded_h, expanded_x:expanded_x+expanded_w]
        
        if roi.size > 0:
            # Detect profile faces in the region
            profile_faces = profile_cascade.detectMultiScale(
                roi,
                scaleFactor=1.1,
                minNeighbors=3,
                minSize=(max(20, w // 2), max(20, h // 2))
            )
            
            # If profile face is detected with high confidence, reject
            if len(profile_faces) > 0:
                # Check if profile face overlaps significantly with frontal face
                for (px, py, pw, ph) in profile_faces:
                    # Adjust coordinates to image space
                    px += expanded_x
                    py += expanded_y
                    # Calculate overlap
                    overlap_x = max(0, min(x + w, px + pw) - max(x, px))
                    overlap_y = max(0, min(y + h, py + ph) - max(y, py))
                    overlap_area = overlap_x * overlap_y
                    face_area = w * h
                    if overlap_area > face_area * 0.5:  # More than 50% overlap
                        return False
    
    # 5. Additional check: Use stricter frontal face detection parameters
    # This ensures we only accept well-detected frontal faces
    strict_faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.15,  # Slightly stricter
        minNeighbors=7,     # Require more neighbors (more confident detection)
        minSize=(max(50, w - 10), max(50, h - 10)),  # Ensure face size is consistent
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # Check if the detected face matches our strict detection
    for (sx, sy, sw, sh) in strict_faces:
        # Check if rectangles overlap significantly
        overlap_x = max(0, min(x + w, sx + sw) - max(x, sx))
        overlap_y = max(0, min(y + h, sy + sh) - max(y, sy))
        overlap_area = overlap_x * overlap_y
        min_area = min(w * h, sw * sh)
        if overlap_area > min_area * 0.7:  # 70% overlap
            return True
    
    # If we get here, the face didn't pass strict detection
    return False


def detect_face(image: np.ndarray) -> bool:
    """
    Detect if a frontal face is present in the image
    Returns True if at least one valid frontal face is detected
    """
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces with standard parameters
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50)  # Increased minimum size for better quality
    )
    
    # Validate each detected face is frontal
    for face in faces:
        if validate_frontal_face(image, face):
            return True
    
    return False


def extract_face_region(image: np.ndarray) -> np.ndarray:
    """
    Extract the face region from the image
    Returns the face region as a numpy array
    Validates that the face is frontal before extraction
    """
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces with stricter parameters
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50)  # Increased minimum size
    )
    
    if len(faces) == 0:
        raise ValueError("No face detected in the image. Please ensure your face is clearly visible and facing the camera.")
    
    # Find the first valid frontal face
    valid_face = None
    for face in faces:
        if validate_frontal_face(image, face):
            valid_face = face
            break
    
    if valid_face is None:
        raise ValueError("No frontal face detected. Please face the camera directly and ensure both eyes are visible. Side/profile poses are not accepted.")
    
    # Get the valid face
    (x, y, w, h) = valid_face
    
    # Extract face region
    face_region = image[y:y+h, x:x+w]
    
    # Resize to standard size (100x100) for comparison
    face_region = cv2.resize(face_region, (100, 100))
    
    return face_region


def compare_faces(stored_face_bytes: bytes, captured_image: np.ndarray, threshold: float = 0.6) -> bool:
    """
    Compare stored face with captured image
    Returns True if faces match (similarity above threshold)
    """
    try:
        # Convert stored bytes to image
        stored_array = np.frombuffer(stored_face_bytes, dtype=np.uint8)
        stored_image = cv2.imdecode(stored_array, cv2.IMREAD_COLOR)
        
        if stored_image is None:
            return False
        
        # Extract face from captured image
        captured_face = extract_face_region(captured_image)
        
        # Resize stored image to same size
        stored_face = cv2.resize(stored_image, (100, 100))
        
        # Convert both to grayscale
        stored_gray = cv2.cvtColor(stored_face, cv2.COLOR_BGR2GRAY)
        captured_gray = cv2.cvtColor(captured_face, cv2.COLOR_BGR2GRAY)
        
        # Calculate histogram similarity
        hist_stored = cv2.calcHist([stored_gray], [0], None, [256], [0, 256])
        hist_captured = cv2.calcHist([captured_gray], [0], None, [256], [0, 256])
        
        # Normalize histograms
        hist_stored = cv2.normalize(hist_stored, hist_stored).flatten()
        hist_captured = cv2.normalize(hist_captured, hist_captured).flatten()
        
        # Calculate correlation
        similarity = cv2.compareHist(hist_stored, hist_captured, cv2.HISTCMP_CORREL)
        
        return similarity >= threshold
        
    except Exception as e:
        print(f"Error comparing faces: {str(e)}")
        return False


def save_face_data(image: np.ndarray) -> bytes:
    """
    Save face region as bytes for storage in database
    """
    face_region = extract_face_region(image)
    
    # Encode as PNG
    success, encoded_image = cv2.imencode('.png', face_region)
    
    if not success:
        raise ValueError("Failed to encode face image")
    
    return encoded_image.tobytes()


def check_duplicate_face(new_face_image: np.ndarray, existing_voters: list[dict], threshold: float = 0.6) -> dict | None:
    """
    Check if the new face matches any existing registered face
    Returns the matching voter dict if found, None otherwise
    """
    try:
        new_face = extract_face_region(new_face_image)
        new_face_resized = cv2.resize(new_face, (100, 100))
        new_face_gray = cv2.cvtColor(new_face_resized, cv2.COLOR_BGR2GRAY)
        new_hist = cv2.calcHist([new_face_gray], [0], None, [256], [0, 256])
        new_hist = cv2.normalize(new_hist, new_hist).flatten()
        
        for voter in existing_voters:
            if not voter.get("face_data"):
                continue
                
            try:
                stored_bytes = voter["face_data"]
                stored_array = np.frombuffer(stored_bytes, dtype=np.uint8)
                stored_image = cv2.imdecode(stored_array, cv2.IMREAD_COLOR)
                
                if stored_image is None:
                    continue
                
                stored_face_resized = cv2.resize(stored_image, (100, 100))
                stored_face_gray = cv2.cvtColor(stored_face_resized, cv2.COLOR_BGR2GRAY)
                stored_hist = cv2.calcHist([stored_face_gray], [0], None, [256], [0, 256])
                stored_hist = cv2.normalize(stored_hist, stored_hist).flatten()
                
                # Calculate similarity
                similarity = cv2.compareHist(new_hist, stored_hist, cv2.HISTCMP_CORREL)
                
                if similarity >= threshold:
                    return voter
                    
            except Exception as e:
                print(f"Error comparing with voter {voter.get('voter_id')}: {str(e)}")
                continue
        
        return None
        
    except Exception as e:
        print(f"Error in check_duplicate_face: {str(e)}")
        return None
