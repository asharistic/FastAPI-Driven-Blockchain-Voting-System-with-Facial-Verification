# 🗳️ Blockchain Voting System with Facial Verification

A secure, transparent voting platform powered by blockchain technology and facial verification, built with FastAPI.

## 📋 Project Overview

This is a university final year project that demonstrates a complete voting system with the following features:

- **Voter Registration**: Register voters with facial capture and unique ID
- **Face Verification**: Verify voter identity using OpenCV face detection before voting
- **Blockchain Storage**: Secure vote storage in an immutable blockchain
- **Admin Dashboard**: View blockchain records, voting results, and voter statistics

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: SQLite with SQLAlchemy ORM
- **Face Detection**: OpenCV with Haar Cascade classifier
- **Blockchain**: Custom Python blockchain implementation
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Templating**: Jinja2

## 📂 Project Structure

```
blockchain-voting-system/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # Database models (Voter, Candidate)
│   ├── database.py          # SQLite connection setup
│   ├── blockchain.py        # Blockchain implementation
│   ├── face_utils.py        # Face detection utilities
│   ├── routes/
│   │   ├── voters.py        # Voter registration & verification
│   │   ├── votes.py         # Voting functionality
│   │   └── admin.py         # Admin dashboard APIs
│   ├── templates/           # HTML templates
│   │   ├── index.html
│   │   ├── register.html
│   │   ├── vote.html
│   │   └── admin.html
│   └── static/              # CSS and JavaScript
│       ├── css/
│       │   └── style.css
│       └── js/
│           ├── register.js
│           ├── vote.js
│           └── admin.js
├── README.md
└── requirements.txt
```

## 🚀 How to Run

### On Replit (Recommended)

1. The application is already configured to run on Replit
2. Click the "Run" button at the top of the Replit workspace
3. The application will start on port 5000
4. Open the webview to access the application

### Locally

1. **Install Python 3.11**

2. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn sqlalchemy opencv-python jinja2 python-multipart pillow numpy
   ```

3. **Run the application**:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 5000 --reload
   ```

4. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

## 📡 API Endpoints

### Voter Management
- `POST /api/register` - Register a new voter with face data
- `POST /api/verify-face` - Verify voter's face before voting
- `GET /api/voters` - Get all registered voters (admin)

### Voting
- `POST /api/vote` - Cast a vote (adds to blockchain)
- `GET /api/candidates` - Get all candidates

### Admin & Blockchain
- `GET /api/chain` - View entire blockchain
- `GET /api/results` - Get voting results
- `GET /health` - Health check endpoint

## 🎯 How to Use the System

### 1. Register as a Voter

1. Go to the **Register** page
2. Enter your full name and unique voter ID
3. Click "Start Camera" and allow camera access
4. Position your face in the camera view
5. Click "Capture Photo" to take your picture
6. Click "Register" to complete registration

### 2. Cast Your Vote

1. Go to the **Vote** page
2. Enter your voter ID
3. Click "Start Camera" and capture your photo for verification
4. Click "Verify Identity"
5. If verification succeeds, select your preferred candidate
6. Click "Vote" to cast your vote
7. Your vote is added to the blockchain

### 3. View Results (Admin)

1. Go to the **Admin Dashboard**
2. View total votes, registered voters, and candidates
3. See detailed voting results with percentages
4. Explore the blockchain to see all blocks
5. Verify blockchain integrity

## 🔒 Security Features

- **Face Verification**: Voters must verify their identity using facial recognition
- **One Vote Per Voter**: System prevents duplicate voting
- **Blockchain Immutability**: All votes are stored in an immutable blockchain
- **Hash Verification**: Each block contains hash of previous block for integrity
- **Timestamp Recording**: All transactions are timestamped

## 🧱 Blockchain Structure

Each block in the blockchain contains:
- **Index**: Block number
- **Timestamp**: When the block was created
- **Data**: Vote information (voter ID, candidate ID, candidate name)
- **Previous Hash**: Hash of the previous block
- **Hash**: SHA-256 hash of current block

## 📊 Sample Data

The system comes pre-loaded with 4 sample candidates:
- Alice Johnson (Progressive Party)
- Bob Smith (Democratic Alliance)
- Carol Williams (Independent)
- David Brown (Green Party)

## 🎓 Educational Purpose

This project is designed for educational purposes and demonstrates:
- FastAPI web framework development
- Database design with SQLAlchemy
- Blockchain implementation in Python
- Face detection with OpenCV
- RESTful API design
- Frontend integration with vanilla JavaScript
- Secure voting system architecture

## 📝 Notes

- The face detection uses OpenCV's Haar Cascade classifier for simplicity
- For production use, consider implementing more robust face recognition (e.g., deep learning models)
- The blockchain implementation is simplified for educational purposes
- In production, implement proper authentication and authorization
- Consider adding encryption for sensitive data

## 🤝 Contributing

This is a university project, but suggestions and improvements are welcome!

## 📄 License

This project is created for educational purposes.

## 👨‍💻 Author

University Final Year Project - 2025

---

**Note**: Make sure to allow camera access in your browser when using the registration and voting features.
