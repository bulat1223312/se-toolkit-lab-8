#!/usr/bin/env python3
"""Fix nanobot Dockerfile and deploy."""

import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    print(f"\n--- {cmd[:70]} ---")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out)
    if err: print(f"STDERR: {err}")
    return out, err

# Create proper Dockerfile
dockerfile = '''FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy and install main dependencies
COPY pyproject.toml ./pyproject.toml
RUN uv pip install --system nanobot-ai pydantic-settings websockets

# Copy MCP packages
COPY mcp/ ./mcp/
RUN uv pip install --system -e ./mcp/

# Copy nanobot-websocket-channel packages
COPY nanobot-websocket-channel/nanobot-channel-protocol/ ./nanobot-websocket-channel/nanobot-channel-protocol/
COPY nanobot-websocket-channel/mcp-webchat/ ./nanobot-websocket-channel/mcp-webchat/
COPY nanobot-websocket-channel/nanobot-webchat/ ./nanobot-websocket-channel/nanobot-webchat/

# Install webchat packages
RUN uv pip install --system -e ./nanobot-websocket-channel/nanobot-channel-protocol/
RUN uv pip install --system -e ./nanobot-websocket-channel/mcp-webchat/
RUN uv pip install --system -e ./nanobot-websocket-channel/nanobot-webchat/

# Copy nanobot app
COPY nanobot/ ./nanobot/

CMD ["python", "/app/nanobot/entrypoint.py"]
'''

run(f"""cat > /root/se-toolkit-lab-8/nanobot/Dockerfile << 'DOCKERFILE'
{dockerfile}
DOCKERFILE""")

run("cat /root/se-toolkit-lab-8/nanobot/Dockerfile")

# Stop nanobot
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop nanobot 2>&1")

# Rebuild nanobot
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot 2>&1 | tail -40", timeout=300)

# Start
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot 2>&1", timeout=60)

time.sleep(15)

# Check status
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps nanobot")

# Check logs
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail 50")

client.close()
