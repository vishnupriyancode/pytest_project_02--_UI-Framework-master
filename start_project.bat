@echo off
echo Starting JSON Processing Project...

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt

:: Create necessary directories
if not exist logs mkdir logs
if not exist output mkdir output
if not exist Edit1_jsons mkdir Edit1_jsons

:: Start the API server
echo Starting API server...
start python api_server.py

:: Wait for API server to start
timeout /t 5

:: Start the frontend (if using React)
if exist api-test-ui (
    echo Starting frontend...
    cd api-test-ui
    start npm start
    cd ..
)

echo Project started successfully!
echo API server running at http://localhost:5000
echo Frontend running at http://localhost:3000 (if React is installed) 