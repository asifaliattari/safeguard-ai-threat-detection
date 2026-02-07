#!/bin/bash

# SafeGuard AI - Local Testing Script
# Test the complete stack locally with Docker Compose

set -e

echo "🧪 SafeGuard AI - Local Testing"
echo "================================"
echo ""

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    echo "Install it from: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "Copy .env.example to .env and fill in your API keys"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Start services
echo "🚀 Starting Docker Compose stack..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
check_service() {
    local name=$1
    local url=$2
    local max_retries=10
    local retry=0

    echo "Checking $name..."

    while [ $retry -lt $max_retries ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            echo "✅ $name is healthy"
            return 0
        fi
        retry=$((retry+1))
        echo "  Attempt $retry/$max_retries..."
        sleep 3
    done

    echo "❌ $name failed health check"
    return 1
}

echo ""
echo "🔍 Health Checks:"
check_service "PostgreSQL" "http://localhost:5432" || true
check_service "Redis" "http://localhost:6379" || true
check_service "Backend API" "http://localhost:8000/health"
check_service "Frontend" "http://localhost:3000"

echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Local stack is running!"
echo ""
echo "🌐 Access Points:"
echo "  Frontend:     http://localhost:3000"
echo "  Backend API:  http://localhost:8000"
echo "  API Docs:     http://localhost:8000/docs"
echo "  Health:       http://localhost:8000/health"
echo ""
echo "📝 View Logs:"
echo "  All:      docker-compose logs -f"
echo "  Backend:  docker-compose logs -f backend"
echo "  Frontend: docker-compose logs -f frontend"
echo ""
echo "🛑 Stop Services:"
echo "  docker-compose down"
echo ""
echo "🧪 Test Detection:"
echo "  1. Open http://localhost:3000"
echo "  2. Click 'Start AI Detection'"
echo "  3. Allow camera permissions"
echo "  4. Test with objects/activities"
echo ""
echo "📊 Run Load Test:"
echo "  python scripts/load-test.py ws://localhost:8000 --users 5 --frames 50"
