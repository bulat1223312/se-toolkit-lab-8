#!/bin/bash
# Task 2 Deployment Script for VM
# Execute this on the VM after copying updated files

set -e

cd /root/se-toolkit-lab-8

echo "=== Task 2 Deployment Script ==="
echo ""

# Check if .env.docker.secret exists
if [ ! -f .env.docker.secret ]; then
    echo "ERROR: .env.docker.secret not found!"
    echo "Please create it first:"
    echo "  cp .env.docker.example .env.docker.secret"
    echo "  nano .env.docker.secret"
    echo ""
    echo "Required variables:"
    echo "  - AUTOCHECKER_API_LOGIN"
    echo "  - AUTOCHECKER_API_PASSWORD"
    echo "  - NANOBOT_ACCESS_KEY"
    echo "  - QWEN_CODE_API_KEY"
    exit 1
fi

echo "Step 1: Stopping existing services..."
docker compose --env-file .env.docker.secret down || true

echo ""
echo "Step 2: Building nanobot service..."
docker compose --env-file .env.docker.secret build nanobot

echo ""
echo "Step 3: Building Flutter client..."
docker compose --env-file .env.docker.secret build client-web-flutter

echo ""
echo "Step 4: Starting all services..."
docker compose --env-file .env.docker.secret up -d

echo ""
echo "Step 5: Checking service status..."
docker compose --env-file .env.docker.secret ps

echo ""
echo "Step 6: Nanobot logs (last 50 lines)..."
docker compose --env-file .env.docker.secret logs nanobot --tail 50

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Next steps:"
echo "1. Open http://$(hostname -I | awk '{print $1}'):42002/flutter in your browser"
echo "2. Login with your NANOBOT_ACCESS_KEY"
echo "3. Test WebSocket: echo '{\"content\":\"Hello\"}' | websocat \"ws://localhost:42002/ws/chat?access_key=YOUR_KEY\""
echo ""
