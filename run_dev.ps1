Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Starting Cloud-Based Student Information Chatbot (CSIC)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 0. Ensure python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    $UserPy = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312"
    if (Test-Path (Join-Path $UserPy "python.exe")) {
        $env:PATH = "$UserPy;$UserPy\Scripts;" + $env:PATH
    }
}

# 1. Initialize database
Write-Host "`n[1/3] Initializing local SQLite database..." -ForegroundColor Yellow
& python database/init_db.py

# 2. Launch backend
Write-Host "`n[2/3] Launching FastAPI Backend on http://localhost:8000..." -ForegroundColor Yellow
$BackendCmd = "if (-not (Get-Command python -ErrorAction SilentlyContinue)) { `$UserPy = Join-Path `$env:LOCALAPPDATA 'Programs\Python\Python312'; if (Test-Path (Join-Path `$UserPy 'python.exe')) { `$env:PATH = `"`$UserPy;`$UserPy\Scripts;`$env:PATH`" } }; python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendCmd

# 3. Launch frontend
Write-Host "`n[3/3] Launching Vite Frontend on http://localhost:5173..." -ForegroundColor Yellow
$FrontendCmd = "if (-not (Get-Command node -ErrorAction SilentlyContinue)) { `$UserNode = Join-Path `$env:USERPROFILE 'node-v20.19.6-win-x64'; if (Test-Path `$UserNode) { `$env:PATH = `"`$UserNode;`$env:PATH`" } }; cd frontend; npm.cmd run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendCmd

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host "CSIC Application Running!" -ForegroundColor Green
Write-Host "Frontend Portal:   http://localhost:5173" -ForegroundColor Green
Write-Host "Backend API Docs:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "`nDemo Accounts (or use 1-click login buttons in browser):" -ForegroundColor Cyan
Write-Host "  Students: rashi@csic.edu, vanshika@csic.edu, silki@csic.edu, akshit@csic.edu / 1234"
Write-Host "  Faculty:  rajesh.kumar@csic.edu (Akshit)  / 1234"
Write-Host "  Admin:    admin@csic.edu (Akshit)         / 1234"
Write-Host "======================================================================`n" -ForegroundColor Green
