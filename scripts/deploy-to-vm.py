#!/usr/bin/env python3
"""Script to fix and deploy the lab on VM via SSH."""

import paramiko
import time
import sys

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

def run_ssh_command(client, command, timeout=60, print_output=True):
    """Run SSH command and return output."""
    if print_output:
        print(f"\n>>> {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err_output = stderr.read().decode('utf-8', errors='replace')
    if print_output:
        if output:
            # Print last 3000 chars for long outputs
            print(output[-3000:] if len(output) > 3000 else output)
        if err_output:
            print(f"ERROR: {err_output[-1000:] if len(err_output) > 1000 else err_output}")
    return output, err_output

def main():
    # Connect to VM
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USERNAME, password=PASSWORD)
    print("Connected!")
    
    # Fix Dockerfile
    print("\n\n=== Fixing nanobot Dockerfile ===")
    dockerfile_content = '''FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./pyproject.toml
RUN uv venv && uv sync --no-dev
COPY . ./nanobot/
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "/app/nanobot/entrypoint.py"]
'''
    # Write Dockerfile using echo
    for line in dockerfile_content.split('\n'):
        escaped = line.replace('"', '\\"').replace('$', '\\$')
        run_ssh_command(client, f'echo "{escaped}" >> /tmp/dockerfile.tmp', print_output=False)
    run_ssh_command(client, 'mv /tmp/dockerfile.tmp /root/se-toolkit-lab-8/nanobot/Dockerfile')
    run_ssh_command(client, 'cat /root/se-toolkit-lab-8/nanobot/Dockerfile')
    
    # Check docker-compose.yml has correct volume mounts
    print("\n\n=== Checking docker-compose.yml nanobot volumes ===")
    run_ssh_command(client, 'grep -A 10 "nanobot:" /root/se-toolkit-lab-8/docker-compose.yml | head -30')
    
    # Build nanobot service
    print("\n\n=== Building nanobot service ===")
    run_ssh_command(client, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot", timeout=300)
    
    # Check build result
    print("\n\n=== Checking build result ===")
    run_ssh_command(client, "docker images | grep nanobot")
    
    # Start all services
    print("\n\n=== Starting all services ===")
    run_ssh_command(client, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d", timeout=120)
    
    # Check status
    print("\n\n=== Checking service status ===")
    run_ssh_command(client, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps")
    
    # Check nanobot logs
    print("\n\n=== Checking nanobot logs ===")
    run_ssh_command(client, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot 2>&1 | tail -50")
    
    # Check if Flutter is served
    print("\n\n=== Checking Flutter endpoint ===")
    run_ssh_command(client, "curl -s http://localhost:42002/flutter/ 2>&1 | head -30")
    
    # Check WebSocket
    print("\n\n=== Checking WebSocket endpoint ===")
    run_ssh_command(client, "curl -s -i http://localhost:42002/ws/chat 2>&1 | head -20")
    
    client.close()
    print("\n\n=== SSH session closed ===")

if __name__ == "__main__":
    main()
