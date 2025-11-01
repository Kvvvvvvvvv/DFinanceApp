@echo off
echo Starting DeFi Loan Portal...

REM Start the Flask backend
cd backend
start "Flask Backend" python app.py

REM Start the React frontend
cd ../frontend/defi-loan-portal
npm start

echo Both servers started. Check your browser for the application.
pause