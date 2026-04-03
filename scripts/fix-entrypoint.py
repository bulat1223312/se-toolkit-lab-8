#!/usr/bin/env python3
"""Fix entrypoint.py to not use opentelemetry-instrument."""

import paramiko

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

# Simpler entrypoint that just runs nanobot gateway
entrypoint_content = '''#!/usr/bin/env python3
"""Entrypoint for nanobot gateway in Docker."""

import json
import os
import sys
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


def main() -> None:
    """Main entrypoint."""
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
        config.setdefault("providers", {}).setdefault("custom", {})["apiKey"] = (
            settings.llm_api_key
        )
    if settings.llm_api_base_url:
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

    # Task 2B: Add webchat channel settings
    config.setdefault("channels", {}).setdefault("webchat", {})["host"] = (
        settings.nanobot_webchat_container_address
    )
    config.setdefault("channels", {}).setdefault("webchat", {})["port"] = (
        settings.nanobot_webchat_container_port
    )

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

    # Launch nanobot gateway
    os.execvp(
        "nanobot",
        ["nanobot", "gateway", "-c", str(resolved_file)],
    )


if __name__ == "__main__":
    main()
'''

print("=== Writing new entrypoint.py ===")
stdin, stdout, stderr = client.exec_command("cat > /root/se-toolkit-lab-8/nanobot/entrypoint.py << 'EOF'" + entrypoint_content + "EOF")
print(stdout.read().decode())

# Verify
print("=== Verifying entrypoint.py ===")
stdin, stdout, stderr = client.exec_command("head -30 /root/se-toolkit-lab-8/nanobot/entrypoint.py")
print(stdout.read().decode())

# Rebuild and restart
print("=== Rebuilding nanobot ===")
stdin, stdout, stderr = client.exec_command("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot 2>&1", timeout=300)
output = stdout.read().decode()
print(output[-2000:] if len(output) > 2000 else output)

print("=== Restarting nanobot ===")
stdin, stdout, stderr = client.exec_command("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot 2>&1")
print(stdout.read().decode())

# Wait and check logs
import time
time.sleep(5)

print("=== Nanobot logs ===")
stdin, stdout, stderr = client.exec_command("docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -30")
print(stdout.read().decode())

client.close()
print("=== Done ===")
