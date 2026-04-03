#!/bin/bash
# FIX SCRIPT - Run this on VM to fix everything

set -e

echo "=== FIXING LAB 8 ==="

cd /root/se-toolkit-lab-8

# 1. Fix pyproject.toml - REMOVE workspace dependencies
echo "1. Fixing pyproject.toml..."
cat > nanobot/pyproject.toml << 'PYPROJECT'
[project]
name = "nanobot"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "nanobot-ai>=0.1.0",
    "pydantic-settings>=2.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
PYPROJECT

# 2. Fix config.json
echo "2. Fixing config.json..."
cat > nanobot/config.json << 'CONFIG'
{
  "providers": {
    "custom": {
      "apiKey": "my-secret-qwen-key",
      "apiBase": "http://qwen-code-api:8080/v1"
    }
  },
  "gateway": {
    "host": "0.0.0.0",
    "port": 18790
  },
  "agents": {
    "defaults": {
      "model": "qwen3-coder-plus"
    }
  },
  "channels": {
    "webchat": {
      "host": "0.0.0.0",
      "port": 8765
    }
  },
  "tools": {
    "mcpServers": {
      "lms": {
        "command": "python",
        "args": ["-m", "mcp_lms"],
        "env": {
          "NANOBOT_LMS_BACKEND_URL": "http://backend:8000",
          "NANOBOT_LMS_API_KEY": "my-secret-api-key"
        }
      },
      "webchat": {
        "command": "python",
        "args": ["-m", "mcp_webchat"],
        "env": {
          "NANOBOT_WS_UI_RELAY_URL": "ws://0.0.0.0:8765",
          "NANOBOT_WS_UI_ACCESS_KEY": "megakey1"
        }
      }
    }
  }
}
CONFIG

# 3. Stop old container
echo "3. Stopping nanobot..."
docker compose --env-file .env.docker.secret stop nanobot || true

# 4. Remove old image
echo "4. Removing old image..."
docker rmi se-toolkit-lab-8-nanobot 2>/dev/null || true

# 5. Rebuild
echo "5. Rebuilding nanobot (this takes 2-3 minutes)..."
docker compose --env-file .env.docker.secret build nanobot

# 6. Start
echo "6. Starting nanobot..."
docker compose --env-file .env.docker.secret up -d --force-recreate nanobot

# 7. Wait
echo "7. Waiting 60 seconds for startup..."
sleep 60

# 8. Verify
echo "8. Verifying..."
echo ""
echo "=== MCP SERVERS ==="
docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep "MCP server.*connected" || echo "MCP not connected yet"

echo ""
echo "=== FLUTTER ==="
curl -s http://localhost:42002/flutter/ | grep -c "Nanobot" || echo "Flutter not ready"

echo ""
echo "=== SERVICES ==="
docker compose --env-file .env.docker.secret ps

echo ""
echo "=== DONE ==="
echo "If you see 'MCP server connected' above, the fix was successful!"
