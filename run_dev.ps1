Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Starting Cloud-Based Student Information Chatbot (CSIC)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Initialize database
Write-Host "`n[1/3] Initializing local SQLite database..." -ForegroundColor Yellow
& python database/init_db.py

# 2. Launch backend
Write-Host "`n[2/3] Launching FastAPI Backend on http://localhost:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

# 3. Launch frontend
Write-Host "`n[3/3] Launching Vite Frontend on http://localhost:5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PATH = 'C:\Users\Mr\node-v20.19.6-win-x64;' + `$env:PATH; cd frontend; npm run dev"

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host "CSIC Application Running!" -ForegroundColor Green
Write-Host "Frontend Portal:   http://localhost:5173" -ForegroundColor Green
Write-Host "Backend API Docs:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "`nDemo Accounts (or use 1-click login buttons in browser):" -ForegroundColor Cyan
Write-Host "  Student: rashi@csic.edu        / 1234"
Write-Host "  Faculty: rajesh.kumar@csic.edu / Faculty@123"
Write-Host "  Admin:   admin@csic.edu        / Admin@123"
Write-Host "======================================================================`n" -ForegroundColor Green
