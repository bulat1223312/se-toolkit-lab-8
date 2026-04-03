#!/usr/bin/env python3
"""
Complete Task 2 fix via SSH with paramiko.
Run this script on Windows - it will connect to VM and fix everything.
"""

import paramiko
import time
import sys

VM_HOST = "10.93.25.49"
VM_USER = "root"
VM_PASSWORD = "23112010A.z"
PROJECT = "/root/se-toolkit-lab-8"

def ssh_connect():
    """Connect to VM via SSH."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        VM_HOST,
        username=VM_USER,
        password=VM_PASSWORD,
        timeout=30,
        allow_agent=False,
        look_for_keys=False
    )
    return client

def run_command(client, command, timeout=120):
    """Run command on VM and return output."""
    print(f"\n{'='*60}")
    print(f"RUNNING: {command[:80]}{'...' if len(command) > 80 else ''}")
    print('='*60)
    
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    
    # Read output
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    
    if output:
        print(output)
    if error and exit_code != 0:
        print(f"STDERR: {error}")
    
    return exit_code, output, error

def main():
    print("=" * 60)
    print("Task 2 - Complete Fix Script")
    print(f"Target: {VM_USER}@{VM_HOST}")
    print("=" * 60)
    
    try:
        client = ssh_connect()
        print("✓ Connected to VM!")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)
    
    try:
        # Step 1: Check current state
        run_command(client, f"cd {PROJECT} && docker compose ps 2>&1 | head -20")
        
        # Step 2: Stop services
        run_command(client, f"cd {PROJECT} && docker compose down 2>&1 | tail -10")
        
        # Step 3: Initialize submodule if needed
        run_command(client, f"cd {PROJECT} && git submodule update --init --recursive 2>&1 | tail -5")
        run_command(client, f"cd {PROJECT} && ls -la nanobot-websocket-channel/ 2>&1 | head -10")
        
        # Step 4: Fix nanobot/pyproject.toml
        run_command(client, f"""cat > {PROJECT}/nanobot/pyproject.toml << 'EOF'
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
EOF
""")
        run_command(client, f"cat {PROJECT}/nanobot/pyproject.toml")
        
        # Step 5: Fix config.json
        run_command(client, f"""cat > {PROJECT}/nanobot/config.json << 'EOF'
{{
  "providers": {{
    "custom": {{
      "apiKey": "${{LLM_API_KEY}}",
      "apiBase": "${{LLM_API_BASE_URL}}"
    }}
  }},
  "gateway": {{
    "host": "0.0.0.0",
    "port": 18790
  }},
  "agents": {{
    "defaults": {{
      "model": "coder-model"
    }}
  }},
  "channels": {{
    "webchat": {{
      "host": "0.0.0.0",
      "port": 8765
    }}
  }},
  "tools": {{
    "mcpServers": {{
      "lms": {{
        "command": "python",
        "args": ["-m", "mcp_lms"],
        "env": {{
          "NANOBOT_LMS_BACKEND_URL": "${{NANOBOT_LMS_BACKEND_URL}}",
          "NANOBOT_LMS_API_KEY": "${{NANOBOT_LMS_API_KEY}}"
        }}
      }}
    }}
  }}
}}
EOF
""")
        run_command(client, f"cat {PROJECT}/nanobot/config.json")
        
        # Step 6: Fix entrypoint.py
        run_command(client, f"""cat > {PROJECT}/nanobot/entrypoint.py << 'ENTRYPOINT'
#!/usr/bin/env python3
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
        sys.exit(f"Error: {{config_file}} not found")
    with open(config_file) as f:
        config = json.load(f)
    settings = Settings()
    if settings.llm_api_key:
        config.setdefault("providers", {{}})["custom"] = {{
            "apiKey": settings.llm_api_key,
            "apiBase": settings.llm_api_base_url or config.get("providers", {{}}).get("custom", {{}}).get("apiBase"),
        }}
    config.setdefault("agents", {{}}).setdefault("defaults", {{}})["model"] = settings.llm_api_model
    config.setdefault("gateway", {{}})["host"] = settings.nanobot_gateway_container_address
    config.setdefault("gateway", {{}})["port"] = settings.nanobot_gateway_container_port
    config.setdefault("channels", {{}}).setdefault("webchat", {{}})["host"] = settings.nanobot_webchat_container_address
    config.setdefault("channels", {{}}).setdefault("webchat", {{}})["port"] = settings.nanobot_webchat_container_port
    config.setdefault("channels", {{}}).setdefault("webchat", {{}})["enabled"] = True
    mcp_servers = config.setdefault("tools", {{}}).setdefault("mcpServers", {{}})
    if settings.nanobot_access_key:
        mcp_servers["webchat"] = {{
            "command": "python",
            "args": ["-m", "mcp_webchat"],
            "env": {{
                "NANOBOT_WS_UI_RELAY_URL": f"ws://{{settings.nanobot_webchat_container_address}}:{{settings.nanobot_webchat_container_port}}",
                "NANOBOT_WS_UI_ACCESS_KEY": settings.nanobot_access_key,
            }},
        }}
    if settings.nanobot_lms_backend_url or settings.nanobot_lms_api_key:
        lms_config = mcp_servers.setdefault("lms", {{}})
        lms_env = lms_config.setdefault("env", {{}})
        if settings.nanobot_lms_backend_url:
            lms_env["NANOBOT_LMS_BACKEND_URL"] = settings.nanobot_lms_backend_url
        if settings.nanobot_lms_api_key:
            lms_env["NANOBOT_LMS_API_KEY"] = settings.nanobot_lms_api_key
    with open(resolved_file, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Using config: {{resolved_file}}")
    print(f"Enabled channels: {{list(config.get('channels', {{}}).keys())}}")
    os.execvp("nanobot", ["nanobot", "gateway", "-c", str(resolved_file)])

if __name__ == "__main__":
    main()
ENTRYPOINT
""")
        run_command(client, f"head -30 {PROJECT}/nanobot/entrypoint.py")
        
        # Step 7: Build and deploy
        run_command(client, f"cd {PROJECT} && docker compose --env-file .env.docker.secret build nanobot 2>&1 | tail -40", timeout=300)
        
        # Step 8: Start services
        run_command(client, f"cd {PROJECT} && docker compose --env-file .env.docker.secret up -d 2>&1 | tail -20", timeout=120)
        
        # Step 9: Check status
        run_command(client, f"cd {PROJECT} && docker compose --env-file .env.docker.secret ps")
        
        # Step 10: Check logs
        run_command(client, f"cd {PROJECT} && docker compose --env-file .env.docker.secret logs nanobot --tail 100")
        
        # Step 11: Test WebSocket
        run_command(client, f"""cd {PROJECT} && ACCESS_KEY=$(grep NANOBOT_ACCESS_KEY .env.docker.secret | cut -d= -f2 | tr -d '[:space:]') && python3 -c "
import asyncio, json, os
async def test():
    try:
        import websockets
        key = os.environ.get('NANOBOT_ACCESS_KEY', '$ACCESS_KEY')
        uri = f'ws://localhost:42002/ws/chat?access_key={{key}}'
        print(f'Connecting to {{uri}}...')
        async with websockets.connect(uri, close_timeout=5) as ws:
            await ws.send(json.dumps({{'content': 'Hello'}}))
            resp = await asyncio.wait_for(ws.recv(), timeout=30)
            print(f'Response: {{resp[:300]}}')
    except Exception as e:
        print(f'Error: {{e}}')
asyncio.run(test())
" 2>&1 || echo 'WebSocket test skipped (websockets not installed)'""")
        
        print("\n" + "="*60)
        print("FIX COMPLETE!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()
        print("\nSSH connection closed.")

if __name__ == "__main__":
    main()
