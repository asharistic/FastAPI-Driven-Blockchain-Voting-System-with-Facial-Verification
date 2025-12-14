# Script to start both backend and frontend servers
Write-Host "Starting Blockchain Voting System..." -ForegroundColor Cyan

# Set PostgreSQL database connection
$env:DATABASE_URL = "postgresql://postgres:1234@localhost:5432/voting_system"
Write-Host "Database connection configured" -ForegroundColor Green

# Set TensorFlow/Keras environment variables for DeepFace compatibility
$env:TF_USE_LEGACY_KERAS = "1"
$env:TF_KERAS = "1"
Write-Host "TensorFlow/Keras compatibility configured" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path ".\.venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment and start backend
Write-Host "`nStarting Backend Server..." -ForegroundColor Green
$dbUrl = $env:DATABASE_URL
$tfKeras = $env:TF_USE_LEGACY_KERAS
$tfKeras2 = $env:TF_KERAS
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; `$env:DATABASE_URL = '$dbUrl'; `$env:TF_USE_LEGACY_KERAS = '$tfKeras'; `$env:TF_KERAS = '$tfKeras2'; .\.venv\Scripts\Activate.ps1; Write-Host 'Backend Server Starting with DeepFace...' -ForegroundColor Green; uvicorn backend.main:app --host 127.0.0.1 --port 5000 --reload"

# Wait for backend to initialize
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend
Write-Host "Starting Frontend Server..." -ForegroundColor Green
if (-not (Test-Path "Frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location Frontend
    npm install
    Set-Location ..
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\Frontend'; Write-Host 'Frontend Server Starting...' -ForegroundColor Green; npm run dev"

Write-Host "`n✅ Both servers are starting!" -ForegroundColor Cyan
Write-Host "`nBackend: http://127.0.0.1:5000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "`nPress any key to exit this window (servers will continue running)..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

