// Registration Page JavaScript
let stream = null;
let capturedImageData = null;

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startCameraBtn = document.getElementById('startCamera');
const capturePhotoBtn = document.getElementById('capturePhoto');
const retakePhotoBtn = document.getElementById('retakePhoto');
const photoPreview = document.getElementById('photoPreview');
const capturedImage = document.getElementById('capturedImage');
const messageDiv = document.getElementById('message');
const registrationForm = document.getElementById('registrationForm');

// Start camera
startCameraBtn.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.style.display = 'block';
        startCameraBtn.style.display = 'none';
        capturePhotoBtn.style.display = 'inline-block';
        showMessage('Camera started. Position your face and click Capture Photo.', 'info');
    } catch (error) {
        showMessage('Error accessing camera: ' + error.message, 'error');
    }
});

// Capture photo
capturePhotoBtn.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    
    capturedImageData = canvas.toDataURL('image/png');
    photoPreview.src = capturedImageData;
    
    video.style.display = 'none';
    capturedImage.style.display = 'block';
    capturePhotoBtn.style.display = 'none';
    retakePhotoBtn.style.display = 'inline-block';
    
    // Stop camera stream
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    
    showMessage('Photo captured successfully!', 'success');
});

// Retake photo
retakePhotoBtn.addEventListener('click', async () => {
    capturedImageData = null;
    capturedImage.style.display = 'none';
    retakePhotoBtn.style.display = 'none';
    
    // Restart camera
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.style.display = 'block';
        capturePhotoBtn.style.display = 'inline-block';
        showMessage('Camera restarted. Capture your photo again.', 'info');
    } catch (error) {
        showMessage('Error accessing camera: ' + error.message, 'error');
    }
});

// Handle form submission
registrationForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const voterName = document.getElementById('voterName').value.trim();
    const voterId = document.getElementById('voterId').value.trim();
    
    if (!voterName || !voterId) {
        showMessage('Please fill in all fields', 'error');
        return;
    }
    
    if (!capturedImageData) {
        showMessage('Please capture your photo before registering', 'error');
        return;
    }
    
    try {
        showMessage('Registering voter...', 'info');
        
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                voter_id: voterId,
                name: voterName,
                face_image: capturedImageData
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message, 'success');
            
            // Reset form after 2 seconds
            setTimeout(() => {
                registrationForm.reset();
                capturedImageData = null;
                capturedImage.style.display = 'none';
                retakePhotoBtn.style.display = 'none';
                startCameraBtn.style.display = 'inline-block';
                messageDiv.style.display = 'none';
            }, 2000);
        } else {
            showMessage(data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    }
});

function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
}
