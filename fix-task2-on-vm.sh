#!/bin/bash
# Task 2 - Full Fix Script for VM
# Run this on the VM: bash /root/se-toolkit-lab-8/fix-task2-on-vm.sh

set -e

cd /root/se-toolkit-lab-8

echo "=== Step 1: Check current Docker state ==="
docker compose ps || true

echo ""
echo "=== Step 2: Stop all services ==="
docker compose down || true

echo ""
echo "=== Step 3: Check nanobot/pyproject.toml ==="
cat nanobot/pyproject.toml

echo ""
echo "=== Step 4: Fix nanobot/pyproject.toml - ensure no workspace references ==="
# The issue is nanobot-ai should NOT be in workspace members
# Check if it's correctly referencing from PyPI
grep -q "nanobot-ai>=0.1.0" nanobot/pyproject.toml && echo "OK: nanobot-ai references PyPI" || echo "WARN: nanobot-ai not found"

echo ""
echo "=== Step 5: Check root pyproject.toml workspace members ==="
grep -A 5 '\[tool.uv.workspace\]' pyproject.toml

echo ""
echo "=== Step 6: Ensure nanobot-websocket-channel is initialized ==="
git submodule status || true
ls -la nanobot-websocket-channel/ || echo "Submodule not initialized!"

echo ""
echo "=== Step 7: Check .env.docker.secret ==="
grep -E "LLM_API_KEY|NANOBOT_ACCESS_KEY|NANOBOT_WEBCHAT|QWEN_CODE_API" .env.docker.secret | head -20

echo ""
echo "=== Step 8: Check config files ==="
echo "--- nanobot/config.json ---"
cat nanobot/config.json

echo ""
echo "--- nanobot/entrypoint.py (first 30 lines) ---"
head -30 nanobot/entrypoint.py

echo ""
echo "=== Step 9: Try building nanobot ==="
docker compose --env-file .env.docker.secret build nanobot 2>&1 | tail -50

echo ""
echo "=== Step 10: If build succeeded, start services ==="
docker compose --env-file .env.docker.secret up -d nanobot 2>&1 | tail -20

echo ""
echo "=== Step 11: Check nanobot logs ==="
docker compose --env-file .env.docker.secret logs nanobot --tail 50

echo ""
echo "=== Step 12: Test WebSocket endpoint ==="
# Get access key
ACCESS_KEY=$(grep NANOBOT_ACCESS_KEY .env.docker.secret | cut -d= -f2)
echo "Testing with access key: ${ACCESS_KEY:0:10}..."

# Use Python to test WebSocket
cd /root/se-toolkit-lab-8
uv run python - <<'PYEOF'
import asyncio
import json
import os

async def test_ws():
    try:
        import websockets
        access_key = os.environ.get("NANOBOT_ACCESS_KEY", "test")
        uri = f"ws://localhost:42002/ws/chat?access_key={access_key}"
        print(f"Connecting to {uri}")
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"content": "Hello"}))
            response = await ws.recv()
            print(f"Response: {response[:200]}")
    except Exception as e:
        print(f"Error: {e}")

# Can't run async directly, need to get env var first
PYEOF

echo ""
echo "=== Step 13: Check Flutter build ==="
docker compose --env-file .env.docker.secret build client-web-flutter 2>&1 | tail -30

echo ""
echo "=== Step 14: Verify Caddy config ==="
cat caddy/Caddyfile

echo ""
echo "=== DONE ==="
