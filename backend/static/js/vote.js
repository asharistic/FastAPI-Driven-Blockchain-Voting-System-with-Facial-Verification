// Voting Page JavaScript
let stream = null;
let capturedImageData = null;
let currentVoterId = null;

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startCameraBtn = document.getElementById('startCamera');
const capturePhotoBtn = document.getElementById('capturePhoto');
const retakePhotoBtn = document.getElementById('retakePhoto');
const photoPreview = document.getElementById('photoPreview');
const capturedImage = document.getElementById('capturedImage');
const messageDiv = document.getElementById('message');
const verificationForm = document.getElementById('verificationForm');
const verificationSection = document.getElementById('verificationSection');
const votingSection = document.getElementById('votingSection');
const candidatesList = document.getElementById('candidatesList');
const voterNameSpan = document.getElementById('voterName');
const voteMessageDiv = document.getElementById('voteMessage');

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

// Handle verification form submission
verificationForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const voterId = document.getElementById('voterId').value.trim();
    
    if (!voterId) {
        showMessage('Please enter your voter ID', 'error');
        return;
    }
    
    if (!capturedImageData) {
        showMessage('Please capture your photo for verification', 'error');
        return;
    }
    
    try {
        showMessage('Verifying your identity...', 'info');
        
        const response = await fetch('/api/verify-face', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                voter_id: voterId,
                face_image: capturedImageData
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentVoterId = voterId;
            voterNameSpan.textContent = data.voter_name;
            verificationSection.style.display = 'none';
            votingSection.style.display = 'block';
            await loadCandidates();
        } else {
            showMessage(data.detail || 'Verification failed', 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    }
});

// Load candidates
async function loadCandidates() {
    try {
        const response = await fetch('/api/candidates');
        const data = await response.json();
        
        if (data.candidates.length === 0) {
            candidatesList.innerHTML = '<p>No candidates available</p>';
            return;
        }
        
        candidatesList.innerHTML = '';
        data.candidates.forEach(candidate => {
            const card = document.createElement('div');
            card.className = 'candidate-card';
            card.innerHTML = `
                <div class="candidate-info">
                    <h4>${candidate.name}</h4>
                    <p>${candidate.party || 'Independent'}</p>
                </div>
                <button class="btn btn-primary" onclick="castVote('${candidate.candidate_id}', '${candidate.name}')">
                    Vote
                </button>
            `;
            candidatesList.appendChild(card);
        });
    } catch (error) {
        showVoteMessage('Error loading candidates: ' + error.message, 'error');
    }
}

// Cast vote
async function castVote(candidateId, candidateName) {
    if (!currentVoterId) {
        showVoteMessage('Please verify your identity first', 'error');
        return;
    }
    
    if (!confirm(`Are you sure you want to vote for ${candidateName}?`)) {
        return;
    }
    
    try {
        showVoteMessage('Casting your vote...', 'info');
        
        const response = await fetch('/api/vote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                voter_id: currentVoterId,
                candidate_id: candidateId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showVoteMessage(data.message + ' Thank you for voting!', 'success');
            candidatesList.innerHTML = '<p class="message success">You have successfully cast your vote. Thank you for participating!</p>';
            
            setTimeout(() => {
                window.location.href = '/';
            }, 3000);
        } else {
            showVoteMessage(data.detail || 'Failed to cast vote', 'error');
        }
    } catch (error) {
        showVoteMessage('Error: ' + error.message, 'error');
    }
}

function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
}

function showVoteMessage(text, type) {
    voteMessageDiv.textContent = text;
    voteMessageDiv.className = `message ${type}`;
}
