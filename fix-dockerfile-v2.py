#!/usr/bin/env python3
"""Fix nanobot Dockerfile with correct paths."""

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

# Create correct Dockerfile using workspace context
dockerfile = '''FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy from workspace (root project) context
COPY --from=workspace pyproject.toml ./pyproject.toml
COPY --from=workspace mcp/ ./mcp/
COPY --from=workspace nanobot-websocket-channel/nanobot-channel-protocol/ ./nanobot-websocket-channel/nanobot-channel-protocol/
COPY --from=workspace nanobot-websocket-channel/mcp-webchat/ ./nanobot-websocket-channel/mcp-webchat/
COPY --from=workspace nanobot-websocket-channel/nanobot-webchat/ ./nanobot-websocket-channel/nanobot-webchat/

# Install MCP packages
RUN uv pip install --system -e ./mcp/
RUN uv pip install --system -e ./nanobot-websocket-channel/nanobot-channel-protocol/
RUN uv pip install --system -e ./nanobot-websocket-channel/mcp-webchat/
RUN uv pip install --system -e ./nanobot-websocket-channel/nanobot-webchat/

# Install main dependencies
RUN uv pip install --system nanobot-ai pydantic-settings websockets

# Copy nanobot app (from local context)
COPY . ./nanobot/

CMD ["python", "/app/nanobot/entrypoint.py"]
'''

run(f"""cat > /root/se-toolkit-lab-8/nanobot/Dockerfile << 'DOCKERFILE'
{dockerfile}
DOCKERFILE""")

run("cat /root/se-toolkit-lab-8/nanobot/Dockerfile")

# Stop and rebuild
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop nanobot 2>&1")

run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot 2>&1 | tail -50", timeout=300)

# Start
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot 2>&1", timeout=60)

time.sleep(15)

# Check logs
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail 60")

client.close()
