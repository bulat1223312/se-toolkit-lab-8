#!/usr/bin/env python3
"""Build and deploy nanobot on VM."""

import paramiko
import time

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

def run_cmd(command, timeout=120, print_output=True):
    if print_output:
        print(f"\n>>> {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    
    # Read output with timeout
    start = time.time()
    output_lines = []
    error_lines = []
    
    while True:
        if stdout.channel.recv_ready():
            data = stdout.channel.recv(4096).decode('utf-8', errors='replace')
            output_lines.append(data)
            if print_output:
                print(data, end='')
            start = time.time()
        elif stderr.channel.recv_ready():
            data = stderr.channel.recv(4096).decode('utf-8', errors='replace')
            error_lines.append(data)
            if print_output:
                print(f"ERR: {data}", end='')
            start = time.time()
        elif stdout.channel.exit_status_ready():
            break
        elif time.time() - start > timeout:
            if print_output:
                print("\n[TIMEOUT]")
            break
        else:
            time.sleep(0.5)
    
    if print_output:
        print()
    return ''.join(output_lines), ''.join(error_lines)

# Check root pyproject.toml workspace members
print("\n=== Root workspace members ===")
run_cmd("grep -A 20 '\\[tool.uv.workspace\\]' /root/se-toolkit-lab-8/pyproject.toml")

# Check if nanobot-websocket-channel packages exist
print("\n=== Checking nanobot-websocket-channel packages ===")
run_cmd("ls -la /root/se-toolkit-lab-8/nanobot-websocket-channel/")

# Build nanobot
print("\n=== Building nanobot service ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot", timeout=300)

# Check images
print("\n=== Checking Docker images ===")
run_cmd("docker images | grep nanobot")

# Start services
print("\n=== Starting all services ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d", timeout=120)

# Check status
print("\n=== Checking service status ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps")

# Check nanobot logs
print("\n=== Checking nanobot logs ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail=50")

# Check Flutter
print("\n=== Checking Flutter endpoint ===")
run_cmd("curl -s http://localhost:42002/flutter/ | head -30")

client.close()
print("\n=== Done ===")
