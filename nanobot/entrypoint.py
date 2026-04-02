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
