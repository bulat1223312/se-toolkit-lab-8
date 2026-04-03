#!/usr/bin/env python3
"""Write entrypoint.py via base64 and restart nanobot."""

import paramiko
import base64
import time

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

def run_cmd(command, timeout=60):
    print(f"\n>>> {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if output:
        print(output[-2000:] if len(output) > 2000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Read local file
with open(r"c:\Users\user\se-toolkit-lab-8\nanobot\entrypoint.py", "rb") as f:
    content = f.read()

# Encode as base64
encoded = base64.b64encode(content).decode()

# Decode and write on VM
print("=== Writing entrypoint.py via base64 ===")
stdin, stdout, stderr = client.exec_command(f'echo "{encoded}" | base64 -d > /root/se-toolkit-lab-8/nanobot/entrypoint.py')
err = stderr.read().decode()
print(f"ERR: {err}" if err else "Success!")

# Verify
print("=== Verifying ===")
run_cmd("wc -l /root/se-toolkit-lab-8/nanobot/entrypoint.py")
run_cmd('grep -c "install_packages" /root/se-toolkit-lab-8/nanobot/entrypoint.py')

# Stop nanobot
print("=== Stopping nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop nanobot")

# Start nanobot
print("=== Starting nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot")

# Wait for package installation
print("Waiting 30 seconds for package installation...")
time.sleep(30)

# Check logs
print("=== Nanobot logs ===")
run_cmd("docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -100")

# Check installed packages
print("=== Installed packages ===")
run_cmd("docker exec se-toolkit-lab-8-nanobot-1 pip list | grep -E 'lms|mcp|nanobot' 2>&1")

# Test WebSocket
print("=== Testing WebSocket ===")
run_cmd("curl -s -i http://localhost:42002/ws/chat 2>&1 | head -10")

client.close()
print("\n=== Done ===")
