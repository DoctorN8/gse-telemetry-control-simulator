@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo GSE Simulator - Quick Start Script
echo ==========================================
echo.

where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Docker is not installed. Please install Docker first.
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

echo Step 1: Stopping any existing containers...
docker-compose down -v

echo.
echo Step 2: Building Docker images...
docker-compose build

echo.
echo Step 3: Starting services...
docker-compose up -d

echo.
echo Step 4: Waiting for services to be ready...
echo   - Waiting for PostgreSQL...
timeout /t 10 /nobreak >nul

echo   - Waiting for backend API...
set /a count=0
:wait_backend
set /a count+=1
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo     Backend is ready!
    goto backend_ready
)
if %count% geq 30 (
    echo     Warning: Backend did not respond in time
    goto backend_ready
)
timeout /t 2 /nobreak >nul
goto wait_backend
:backend_ready

echo   - Waiting for frontend...
set /a count=0
:wait_frontend
set /a count+=1
curl -s http://localhost:8501 >nul 2>&1
if %errorlevel% equ 0 (
    echo     Frontend is ready!
    goto frontend_ready
)
if %count% geq 30 (
    echo     Warning: Frontend did not respond in time
    goto frontend_ready
)
timeout /t 2 /nobreak >nul
goto wait_frontend
:frontend_ready

echo.
echo ==========================================
echo GSE Simulator is now running!
echo ==========================================
echo.
echo Access the following services:
echo   - Main Dashboard:     http://localhost:8501
echo   - RAG Assistant:      http://localhost:8502
echo   - Backend API:        http://localhost:8000
echo   - API Documentation:  http://localhost:8000/docs
echo.
echo To view logs:
echo   docker-compose logs -f
echo.
echo To stop the system:
echo   docker-compose down
echo.
echo To run tests:
echo   cd tests ^&^& pip install -r requirements.txt ^&^& pytest test_integration.py -v
echo.

pause
