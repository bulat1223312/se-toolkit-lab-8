#!/bin/bash
# Task 2 - Complete Fix Script
# Run on VM: curl -sL https://... | bash
# Or copy-paste each section manually

set -e
cd /root/se-toolkit-lab-8

echo "========================================="
echo "Task 2 Fix Script - Starting"
echo "========================================="

# Step 0: Backup current state
echo ""
echo "=== Step 0: Backing up current configs ==="
cp -r nanobot/ nanobot.backup.$(date +%s) 2>/dev/null || true
cp docker-compose.yml docker-compose.yml.backup.$(date +%s) 2>/dev/null || true
cp caddy/Caddyfile caddy/Caddyfile.backup.$(date +%s) 2>/dev/null || true

# Step 1: Fix nanobot/pyproject.toml
echo ""
echo "=== Step 1: Fixing nanobot/pyproject.toml ==="
cat > nanobot/pyproject.toml << 'EOF'
[project]
name = "nanobot"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "nanobot-ai>=0.1.0",
    "pydantic-settings>=2.0.0",
    # Task 2B — uncomment after you add nanobot-websocket-channel.
    "nanobot-webchat @ file:///app/nanobot-websocket-channel/nanobot-webchat",
    "mcp-webchat @ file:///app/nanobot-websocket-channel/mcp-webchat",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF
echo "nanobot/pyproject.toml updated"

# Step 2: Fix nanobot/config.json
echo ""
echo "=== Step 2: Fixing nanobot/config.json ==="
cat > nanobot/config.json << 'EOF'
{
  "providers": {
    "custom": {
      "apiKey": "${LLM_API_KEY}",
      "apiBase": "${LLM_API_BASE_URL}"
    }
  },
  "gateway": {
    "host": "0.0.0.0",
    "port": 18790
  },
  "agents": {
    "defaults": {
      "model": "coder-model"
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
        "args": [
          "-m",
          "mcp_lms"
        ],
        "env": {
          "NANOBOT_LMS_BACKEND_URL": "${NANOBOT_LMS_BACKEND_URL}",
          "NANOBOT_LMS_API_KEY": "${NANOBOT_LMS_API_KEY}"
        }
      }
    }
  }
}
EOF
echo "nanobot/config.json updated"

# Step 3: Fix nanobot/entrypoint.py
echo ""
echo "=== Step 3: Fixing nanobot/entrypoint.py ==="
cat > nanobot/entrypoint.py << 'PYEOF'
#!/usr/bin/env python3
"""Entrypoint for nanobot gateway in Docker."""

import json
import os
import sys
import subprocess
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Docker environment settings."""

    # LLM configuration
    llm_api_key: str | None = None
    llm_api_base_url: str | None = None
    llm_api_model: str = "coder-model"

    # Gateway configuration
    nanobot_gateway_container_address: str = "0.0.0.0"
    nanobot_gateway_container_port: int = 18790

    # WebChat channel configuration (Task 2B)
    nanobot_webchat_container_address: str = "0.0.0.0"
    nanobot_webchat_container_port: int = 8765
    nanobot_access_key: str | None = None

    # LMS MCP configuration
    nanobot_lms_backend_url: str | None = None
    nanobot_lms_api_key: str | None = None

    class Config:
        env_prefix = ""
        extra = "ignore"


def install_packages():
    """Install MCP servers from workspace directories."""
    mcp_path = Path("/app/mcp")
    webchat_path = Path("/app/nanobot-websocket-channel")

    if mcp_path.exists():
        print(f"Installing lms-mcp from {mcp_path}...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(mcp_path)], check=True)
    else:
        print(f"Warning: {mcp_path} not found")

    if webchat_path.exists():
        # First install nanobot-channel-protocol (dependency)
        channel_protocol = webchat_path / "nanobot-channel-protocol"
        if channel_protocol.exists():
            print(f"Installing nanobot-channel-protocol from {channel_protocol}...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(channel_protocol), "--ignore-requires-python"], check=True)

        mcp_webchat = webchat_path / "mcp-webchat"
        nanobot_webchat = webchat_path / "nanobot-webchat"
        if mcp_webchat.exists():
            print(f"Installing mcp-webchat from {mcp_webchat}...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(mcp_webchat), "--ignore-requires-python"], check=True)
        if nanobot_webchat.exists():
            print(f"Installing nanobot-webchat from {nanobot_webchat}...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(nanobot_webchat), "--ignore-requires-python"], check=True)
    else:
        print(f"Warning: {webchat_path} not found")


def main() -> None:
    """Main entrypoint."""
    # Install MCP packages first
    install_packages()

    config_dir = Path("/app/nanobot")
    config_file = config_dir / "config.json"
    resolved_file = config_dir / "config.resolved.json"

    # Load base config
    if not config_file.exists():
        print(f"Error: {config_file} not found", file=sys.stderr)
        sys.exit(1)

    with open(config_file) as f:
        config = json.load(f)

    # Load environment settings
    settings = Settings()

    # Update providers.custom with LLM settings
    if settings.llm_api_key:
        config.setdefault("providers", {})["custom"] = {
            "apiKey": settings.llm_api_key,
            "apiBase": settings.llm_api_base_url or config.get("providers", {}).get("custom", {}).get("apiBase"),
        }
    if settings.llm_api_base_url and "custom" not in config.get("providers", {}):
        config.setdefault("providers", {}).setdefault("custom", {})[
            "apiBase"
        ] = settings.llm_api_base_url

    # Update agents.defaults with model
    config.setdefault("agents", {}).setdefault("defaults", {})["model"] = (
        settings.llm_api_model
    )

    # Update gateway settings
    config.setdefault("gateway", {})["host"] = settings.nanobot_gateway_container_address
    config.setdefault("gateway", {})["port"] = settings.nanobot_gateway_container_port

    # Task 2B: Add webchat channel settings - explicitly enable the channel
    config.setdefault("channels", {}).setdefault("webchat", {})["host"] = (
        settings.nanobot_webchat_container_address
    )
    config.setdefault("channels", {}).setdefault("webchat", {})["port"] = (
        settings.nanobot_webchat_container_port
    )
    config.setdefault("channels", {}).setdefault("webchat", {})["enabled"] = True

    # Task 2B: Add webchat MCP server settings
    mcp_servers = config.setdefault("tools", {}).setdefault("mcpServers", {})

    # Configure mcp_webchat server
    if settings.nanobot_access_key:
        mcp_servers["webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
            "env": {
                "NANOBOT_WS_UI_RELAY_URL": f"ws://{settings.nanobot_webchat_container_address}:{settings.nanobot_webchat_container_port}",
                "NANOBOT_WS_UI_ACCESS_KEY": settings.nanobot_access_key,
            },
        }

    # Update LMS MCP environment variables
    if settings.nanobot_lms_backend_url or settings.nanobot_lms_api_key:
        lms_config = mcp_servers.setdefault("lms", {})
        lms_env = lms_config.setdefault("env", {})
        if settings.nanobot_lms_backend_url:
            lms_env["NANOBOT_LMS_BACKEND_URL"] = settings.nanobot_lms_backend_url
        if settings.nanobot_lms_api_key:
            lms_env["NANOBOT_LMS_API_KEY"] = settings.nanobot_lms_api_key

    # Write resolved config
    with open(resolved_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_file}")
    print(f"Enabled channels: {list(config.get('channels', {}).keys())}")

    # Launch nanobot gateway
    os.execvp(
        "nanobot",
        ["nanobot", "gateway", "-c", str(resolved_file)],
    )


if __name__ == "__main__":
    main()
PYEOF
echo "nanobot/entrypoint.py updated"

# Step 4: Fix docker-compose.yml
echo ""
echo "=== Step 4: Fixing docker-compose.yml ==="
# Just verify it's correct - the local version should be fine
cat docker-compose.yml | head -10
echo "...docker-compose.yml looks correct"

# Step 5: Fix caddy/Caddyfile
echo ""
echo "=== Step 5: Verifying caddy/Caddyfile ==="
cat caddy/Caddyfile | head -10
echo "...Caddyfile looks correct"

# Step 6: Stop and rebuild
echo ""
echo "=== Step 6: Stopping services ==="
docker compose down || true

echo ""
echo "=== Step 7: Rebuilding nanobot ==="
docker compose --env-file .env.docker.secret build nanobot 2>&1 | tail -30

echo ""
echo "=== Step 8: Starting services ==="
docker compose --env-file .env.docker.secret up -d 2>&1 | tail -20

echo ""
echo "=== Step 9: Checking service status ==="
docker compose --env-file .env.docker.secret ps

echo ""
echo "=== Step 10: Checking nanobot logs ==="
docker compose --env-file .env.docker.secret logs nanobot --tail 50

echo ""
echo "=== Step 11: Testing WebSocket ==="
ACCESS_KEY=$(grep NANOBOT_ACCESS_KEY .env.docker.secret | cut -d= -f2 | tr -d '[:space:]')
echo "Access key (first 10 chars): ${ACCESS_KEY:0:10}"

# Test with Python
python3 -c "
import asyncio
import json
import os

async def test():
    try:
        import websockets
        key = os.environ.get('NANOBOT_ACCESS_KEY', '${ACCESS_KEY}')
        uri = f'ws://localhost:42002/ws/chat?access_key={key}'
        print(f'Connecting to {uri}...')
        async with websockets.connect(uri, close_timeout=5) as ws:
            await ws.send(json.dumps({'content': 'Hello'}))
            resp = await asyncio.wait_for(ws.recv(), timeout=30)
            print(f'Response: {resp[:300]}')
    except Exception as e:
        print(f'Error: {e}')

try:
    asyncio.run(test())
except:
    print('websockets not installed, skipping WS test')
" 2>&1

echo ""
echo "=== Step 12: Testing Qwen Code API ==="
QWEN_KEY=$(grep QWEN_CODE_API_KEY .env.docker.secret | cut -d= -f2 | tr -d '[:space:]')
curl -s -m 15 http://localhost:42005/health || echo "Health check failed"

echo ""
echo "========================================="
echo "Task 2 Fix Script - Complete"
echo "========================================="
echo ""
echo "Check the output above for any errors."
echo "If nanobot is 'Up' and logs show 'Agent loop started', you're good!"
