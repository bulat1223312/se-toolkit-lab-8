#!/usr/bin/env python3
"""Upload fixed entrypoint.py and test."""

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
        print(output[-5000:] if len(output) > 5000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Read local file
with open(r"c:\Users\user\se-toolkit-lab-8\nanobot\entrypoint.py", "rb") as f:
    content = f.read()

# Encode as base64
encoded = base64.b64encode(content).decode()

# Decode and write on VM
print("=== Writing entrypoint.py ===")
stdin, stdout, stderr = client.exec_command(f'echo "{encoded}" | base64 -d > /root/se-toolkit-lab-8/nanobot/entrypoint.py')
err = stderr.read().decode()
print(f"ERR: {err}" if err else "Success!")

# Verify
print("=== Verifying install_packages ===")
run_cmd('grep -A 3 "nanobot-channel-protocol" /root/se-toolkit-lab-8/nanobot/entrypoint.py')

# Restart nanobot
print("=== Restarting nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot")

# Wait for installation
print("Waiting 40 seconds...")
time.sleep(40)

# Check logs
print("=== Nanobot logs ===")
run_cmd("docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -150")

# Check installed packages
print("=== Installed packages ===")
run_cmd("docker exec se-toolkit-lab-8-nanobot-1 pip list | grep -E 'lms|mcp|nanobot' 2>&1")

# Test WebSocket with access key
print("=== Testing WebSocket ===")
run_cmd("curl -s -i 'http://localhost:42002/ws/chat?access_key=megakey1' -H 'Connection: Upgrade' 2>&1 | head -15")

# Check Flutter
print("=== Checking Flutter ===")
run_cmd("curl -s http://localhost:42002/flutter/ 2>&1 | head -30")

client.close()
print("\n=== Done ===")
