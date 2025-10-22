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


def detect_face(image: np.ndarray) -> bool:
    """
    Detect if a face is present in the image
    Returns True if at least one face is detected
    """
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    return len(faces) > 0


def extract_face_region(image: np.ndarray) -> np.ndarray:
    """
    Extract the face region from the image
    Returns the face region as a numpy array
    """
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    if len(faces) == 0:
        raise ValueError("No face detected in the image")
    
    # Get the first (largest) face
    (x, y, w, h) = faces[0]
    
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
