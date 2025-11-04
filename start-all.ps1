# Script to start both backend and frontend servers
Write-Host "Starting Blockchain Voting System..." -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path ".\.venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment and start backend
Write-Host "`nStarting Backend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\Activate.ps1; Write-Host 'Backend Server Starting...' -ForegroundColor Green; uvicorn backend.main:app --host 127.0.0.1 --port 5000 --reload"

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

