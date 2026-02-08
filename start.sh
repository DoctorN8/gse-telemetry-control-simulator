#!/bin/bash

set -e

echo "=========================================="
echo "GSE Simulator - Quick Start Script"
echo "=========================================="
echo ""

if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "Step 1: Stopping any existing containers..."
docker-compose down -v

echo ""
echo "Step 2: Building Docker images..."
docker-compose build

echo ""
echo "Step 3: Starting services..."
docker-compose up -d

echo ""
echo "Step 4: Waiting for services to be ready..."
echo "  - Waiting for PostgreSQL..."
sleep 10

echo "  - Waiting for backend API..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "    Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "    Warning: Backend did not respond in time"
    fi
    sleep 2
done

echo "  - Waiting for frontend..."
for i in {1..30}; do
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "    Frontend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "    Warning: Frontend did not respond in time"
    fi
    sleep 2
done

echo ""
echo "=========================================="
echo "GSE Simulator is now running!"
echo "=========================================="
echo ""
echo "Access the following services:"
echo "  - Main Dashboard:     http://localhost:8501"
echo "  - RAG Assistant:      http://localhost:8502"
echo "  - Backend API:        http://localhost:8000"
echo "  - API Documentation:  http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop the system:"
echo "  docker-compose down"
echo ""
echo "To run tests:"
echo "  cd tests && pip install -r requirements.txt && pytest test_integration.py -v"
echo ""
