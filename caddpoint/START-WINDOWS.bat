
@echo off
title Skill Pro - Django Server

echo ==========================================
echo       CADPOINT SKILL PRO - STARTING
echo ==========================================

cd /d "%~dp0skillpro_django"

if not exist manage.py (
    echo ERROR: manage.py not found!
    echo Check the skillpro_django folder location.
    pause
    exit /b 1
)

echo.
echo [1/5] Checking Python...

python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    pause
    exit /b 1
)

echo.
echo [2/5] Creating virtual environment...

if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Virtual environment creation failed.
        pause
        exit /b 1
    )
)

echo.
echo [3/5] Activating virtual environment...

call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Virtual environment activation failed.
    pause
    exit /b 1
)

echo.
echo [4/5] Installing required packages...

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Package installation failed.
    pause
    exit /b 1
)

echo.
echo [5/5] Preparing database...

python manage.py migrate

if errorlevel 1 (
    echo ERROR: Database migration failed.
    pause
    exit /b 1
)

echo.
echo Creating or checking admin account...

python manage.py ensure_admin

if errorlevel 1 (
    echo ERROR: Admin account setup failed.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo WEBSITE: http://127.0.0.1:8000/
echo DASHBOARD:
echo http://127.0.0.1:8000/students-details/skillpro-dashboard.html
echo ==========================================

echo Starting Django server...

python manage.py runserver 8000

pause
