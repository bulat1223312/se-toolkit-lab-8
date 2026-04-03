# Complete fix for Task 2
# Copy this entire script to the VM and run: bash fix-task2-complete.sh

set -ex
cd /root/se-toolkit-lab-8

echo "=== Step 0: Backup ==="
cp -r nanobot/ nanobot.backup.$(date +%s) 2>/dev/null || true

echo "=== Step 1: Verify submodule ==="
git submodule update --init --recursive 2>/dev/null || true
ls -la nanobot-websocket-channel/ || { echo "ERROR: submodule missing!"; exit 1; }

echo "=== Step 2: Fix pyproject.toml ==="
cat > nanobot/pyproject.toml << 'PYPROJECT'
[project]
name = "nanobot"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "nanobot-ai>=0.1.0",
    "pydantic-settings>=2.0.0",
    # Task 2B
    "nanobot-webchat @ file:///app/nanobot-websocket-channel/nanobot-webchat",
    "mcp-webchat @ file:///app/nanobot-websocket-channel/mcp-webchat",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
PYPROJECT

echo "=== Step 3: Fix config.json ==="
cat > nanobot/config.json << 'CONFIG'
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
        "args": ["-m", "mcp_lms"],
        "env": {
          "NANOBOT_LMS_BACKEND_URL": "${NANOBOT_LMS_BACKEND_URL}",
          "NANOBOT_LMS_API_KEY": "${NANOBOT_LMS_API_KEY}"
        }
      }
    }
  }
}
CONFIG

echo "=== Step 4: Fix entrypoint.py ==="
cat > nanobot/entrypoint.py << 'ENTRYPOINT'
#!/usr/bin/env python3
"""Entrypoint for nanobot gateway in Docker."""
import json, os, sys, subprocess
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm_api_key: str | None = None
    llm_api_base_url: str | None = None
    llm_api_model: str = "coder-model"
    nanobot_gateway_container_address: str = "0.0.0.0"
    nanobot_gateway_container_port: int = 18790
    nanobot_webchat_container_address: str = "0.0.0.0"
    nanobot_webchat_container_port: int = 8765
    nanobot_access_key: str | None = None
    nanobot_lms_backend_url: str | None = None
    nanobot_lms_api_key: str | None = None
    class Config:
        env_prefix = ""
        extra = "ignore"

def install_packages():
    mcp_path = Path("/app/mcp")
    webchat_path = Path("/app/nanobot-websocket-channel")
    if mcp_path.exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(mcp_path)], check=True)
    if webchat_path.exists():
        for pkg in ["nanobot-channel-protocol", "mcp-webchat", "nanobot-webchat"]:
            p = webchat_path / pkg
            if p.exists():
                subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(p), "--ignore-requires-python"], check=True)

def main():
    install_packages()
    config_dir = Path("/app/nanobot")
    config_file = config_dir / "config.json"
    resolved_file = config_dir / "config.resolved.json"
    if not config_file.exists():
        sys.exit(f"Error: {config_file} not found")
    with open(config_file) as f:
        config = json.load(f)
    settings = Settings()
    
    if settings.llm_api_key:
        config.setdefault("providers", {})["custom"] = {
            "apiKey": settings.llm_api_key,
            "apiBase": settings.llm_api_base_url or config.get("providers", {}).get("custom", {}).get("apiBase"),
        }
    config.setdefault("agents", {}).setdefault("defaults", {})["model"] = settings.llm_api_model
    config.setdefault("gateway", {})["host"] = settings.nanobot_gateway_container_address
    config.setdefault("gateway", {})["port"] = settings.nanobot_gateway_container_port
    
    # Webchat channel
    config.setdefault("channels", {}).setdefault("webchat", {})["host"] = settings.nanobot_webchat_container_address
    config.setdefault("channels", {}).setdefault("webchat", {})["port"] = settings.nanobot_webchat_container_port
    config.setdefault("channels", {}).setdefault("webchat", {})["enabled"] = True
    
    # MCP servers
    mcp_servers = config.setdefault("tools", {}).setdefault("mcpServers", {})
    if settings.nanobot_access_key:
        mcp_servers["webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
            "env": {
                "NANOBOT_WS_UI_RELAY_URL": f"ws://{settings.nanobot_webchat_container_address}:{settings.nanobot_webchat_container_port}",
                "NANOBOT_WS_UI_ACCESS_KEY": settings.nanobot_access_key,
            },
        }
    if settings.nanobot_lms_backend_url or settings.nanobot_lms_api_key:
        lms_config = mcp_servers.setdefault("lms", {})
        lms_env = lms_config.setdefault("env", {})
        if settings.nanobot_lms_backend_url:
            lms_env["NANOBOT_LMS_BACKEND_URL"] = settings.nanobot_lms_backend_url
        if settings.nanobot_lms_api_key:
            lms_env["NANOBOT_LMS_API_KEY"] = settings.nanobot_lms_api_key
    
    with open(resolved_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Using config: {resolved_file}")
    print(f"Enabled channels: {list(config.get('channels', {}).keys())}")
    os.execvp("nanobot", ["nanobot", "gateway", "-c", str(resolved_file)])

if __name__ == "__main__":
    main()
ENTRYPOINT

echo "=== Step 5: Stop services ==="
docker compose down || true

echo "=== Step 6: Build and start ==="
docker compose --env-file .env.docker.secret build nanobot 2>&1 | tail -30
docker compose --env-file .env.docker.secret up -d 2>&1 | tail -20

echo "=== Step 7: Check status ==="
docker compose --env-file .env.docker.secret ps
docker compose --env-file .env.docker.secret logs nanobot --tail 50

echo "=== DONE ==="
