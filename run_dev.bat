@echo off
echo ======================================================================
echo Starting Cloud-Based Student Information Chatbot (CSIC)
echo ======================================================================
echo.

echo [1/3] Initializing local SQLite database...
python database\init_db.py

echo [2/3] Launching FastAPI Backend on http://localhost:8000...
start "CSIC Backend (FastAPI)" cmd /k "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [3/3] Launching Vite Frontend on http://localhost:5173...
start "CSIC Frontend (React)" cmd /k "set PATH=C:\Users\Mr\node-v20.19.6-win-x64;%PATH% && cd frontend && npm run dev"

echo.
echo ======================================================================
echo System successfully launched!
echo - Web Application:   http://localhost:5173
echo - API Documentation: http://localhost:8000/docs
echo.
echo Demo Test Credentials:
echo - Student: aarav.sharma@csic.edu  / Student@123
echo - Faculty: rajesh.kumar@csic.edu  / Faculty@123
echo - Admin:   admin@csic.edu         / Admin@123
echo (Or use the 1-click Quick Login buttons on the login page)
echo ======================================================================
pause
