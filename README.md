# 🗳️ Blockchain Voting System with Facial Verification

A secure, transparent voting platform powered by blockchain technology and facial verification, built with FastAPI.

## 📋 Project Overview

This is a university final year project that demonstrates a complete voting system with the following features:

- **Voter Registration**: Register voters with facial capture and unique ID using DeepFace (FaceNet)
- **Face Verification**: Verify voter identity using deep learning face recognition (DeepFace FaceNet model)
- **Blockchain Storage**: Secure vote storage in an immutable blockchain
- **Admin Dashboard**: View blockchain records, voting results, and voter statistics

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (using psycopg)
- **Face Recognition**: DeepFace with FaceNet model (deep learning)
- **Blockchain**: Custom Python blockchain implementation
- **Frontend**: React 18 with Vite, React Router
- **Authentication**: JWT tokens
- **API Communication**: Axios

## 📂 Project Structure

```
FaceVoteChain/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # PostgreSQL database helpers
│   ├── blockchain.py        # Blockchain implementation
│   ├── face_utils.py        # Face detection utilities
│   ├── auth.py              # JWT authentication
│   ├── routes/
│   │   ├── voters.py        # Voter registration & verification
│   │   ├── votes.py         # Voting functionality
│   │   ├── admin.py         # Admin APIs
│   │   ├── admin_enhanced.py # Enhanced admin CRUD APIs
│   │   └── auth.py          # Authentication routes
│   └── (PostgreSQL database - external)
├── Frontend/                # React frontend application
│   ├── src/
│   │   ├── pages/           # Page components
│   │   │   ├── Home.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Vote.jsx
│   │   │   └── admin/
│   │   ├── components/      # Reusable components
│   │   ├── services/        # API service layer
│   │   └── App.jsx          # Main app component
│   ├── package.json
│   └── vite.config.js
├── README.md
├── requirements.txt         # Python dependencies
└── start-all.ps1           # Windows startup script
```

## 🚀 How to Run Locally (Windows)

1. **Install Python 3.11**

2. **Create and activate a virtual environment**
   ```powershell
   cd C:\Users\HP\Downloads\FaceVoteChain
   python -m venv .venv
   . .\.venv\Scripts\Activate.ps1
   ```

3. **Install PostgreSQL**
   - Download and install PostgreSQL from https://www.postgresql.org/download/
   - Create a database named `voting_system` (or your preferred name)
   - Note your PostgreSQL username, password, host, and port (default port is 5432)

4. **Set up database connection**
   - The `start-all.ps1` script automatically sets the DATABASE_URL
   - If running manually, set the environment variable:
   ```powershell
   $env:DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/voting_system"
   ```
   - Replace `YOUR_PASSWORD` with your PostgreSQL password
   - The database tables will be created automatically on first run

5. **Install dependencies**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. **Run the application**
   - **Option 1: Use the start script (recommended)**
     ```powershell
     .\start-all.ps1
     ```
     This will start both backend and frontend servers automatically.
   
   - **Option 2: Run manually**
     ```powershell
     # Terminal 1 - Backend
     $env:DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/voting_system"
     uvicorn backend.main:app --host 127.0.0.1 --port 5000 --reload
     
     # Terminal 2 - Frontend
     cd Frontend
     npm install  # Only needed first time
     npm run dev
     ```

7. **Access the application**
   - Frontend: Open your browser and navigate to `http://localhost:3000`
   - Backend API: `http://127.0.0.1:5000`
   - API Docs: `http://127.0.0.1:5000/docs`

## 📡 API Endpoints

### Voter Management
- `POST /api/register` - Register a new voter with face data
- `POST /api/verify-face` - Verify voter's face before voting
- `GET /api/voters` - Get all registered voters (admin)

### Voting
- `POST /api/vote` - Cast a vote (adds to blockchain)
- `GET /api/candidates` - Get all candidates

### Admin & Blockchain (JWT Auth Required)
- `GET /api/admin/stats` - Get dashboard statistics
- `GET /api/admin/elections` - Get all elections (CRUD available)
- `GET /api/admin/candidates` - Get all candidates (CRUD available)
- `GET /api/admin/voters` - Get all voters
- `GET /api/admin/blockchain` - View entire blockchain
- `GET /api/admin/results` - Get voting results
- `POST /api/auth/login` - Admin login
- `GET /health` - Health check endpoint

## 🎨 React Frontend

The project includes a modern React frontend in the `Frontend/` directory.

### Start Frontend
```powershell
cd Frontend
npm install
npm run dev
```

### Start Both Servers
```powershell
# Use the convenience script
.\start-all.ps1

# Or manually start both servers in separate terminals
```

Frontend URL: `http://localhost:3000`
Backend URL: `http://127.0.0.1:5000`

See `Frontend/README.md` and `Frontend/CONNECTION_GUIDE.md` for details.

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
- Database design with PostgreSQL
- Blockchain implementation in Python
- Face detection with OpenCV
- RESTful API design
- Frontend integration with React with Vite 18
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
