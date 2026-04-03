#!/usr/bin/env python3
"""Rebuild nanobot with simple Dockerfile."""

import paramiko
import time

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)
sftp = client.open_sftp()

def run_cmd(command, timeout=60):
    print(f"\n>>> {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if output:
        print(output[-3000:] if len(output) > 3000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Upload simple Dockerfile
dockerfile = '''FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./pyproject.toml
RUN uv pip install --system nanobot-ai pydantic-settings
COPY . ./nanobot/
CMD ["python", "/app/nanobot/entrypoint.py"]
'''

print("=== Uploading simple Dockerfile ===")
stdin, stdout, stderr = client.exec_command("echo '" + dockerfile.replace("'", "'\"'\"'") + "' > /root/se-toolkit-lab-8/nanobot/Dockerfile")
print(stdout.read().decode())

# Verify
print("=== Verifying Dockerfile ===")
run_cmd("cat /root/se-toolkit-lab-8/nanobot/Dockerfile")

# Stop
print("\n=== Stopping nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop nanobot")

# Rebuild with --no-cache
print("\n=== Rebuilding with --no-cache ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot --no-cache 2>&1", timeout=300)

# Start
print("\n=== Starting nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d --force-recreate nanobot")

# Wait for package installation
print("Waiting 20 seconds...")
time.sleep(20)

# Check logs
print("\n=== Nanobot logs ===")
run_cmd("docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -100")

# Check if modules installed
print("\n=== Checking modules ===")
run_cmd("docker exec se-toolkit-lab-8-nanobot-1 python -c 'import lms_mcp; print(\"lms_mcp OK\")' 2>&1")
run_cmd("docker exec se-toolkit-lab-8-nanobot-1 python -c 'import mcp_webchat; print(\"mcp_webchat OK\")' 2>&1")

# Test WebSocket
print("\n=== Testing WebSocket ===")
run_cmd("curl -s -i http://localhost:42002/ws/chat 2>&1 | head -10")

# Check Flutter
print("\n=== Checking Flutter ===")
run_cmd("curl -s http://localhost:42002/flutter/ | head -20")

sftp.close()
client.close()
print("\n=== Done ===")
