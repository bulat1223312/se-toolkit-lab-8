#!/usr/bin/env python3
"""Final test with --ignore-requires-python."""

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
        print(output[-6000:] if len(output) > 6000 else output)
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
print("=== Verifying ===")
run_cmd('grep "ignore-requires-python" /root/se-toolkit-lab-8/nanobot/entrypoint.py')

# Restart nanobot
print("=== Restarting nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot")

# Wait for installation
print("Waiting 50 seconds...")
time.sleep(50)

# Check logs
print("=== Nanobot logs ===")
run_cmd("docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -200")

# Check installed packages
print("=== Installed packages ===")
run_cmd("docker exec se-toolkit-lab-8-nanobot-1 pip list | grep -Ei 'lms|mcp|nanobot' 2>&1")

# Test WebSocket
print("=== Testing WebSocket ===")
run_cmd("curl -s -i 'http://localhost:42002/ws/chat?access_key=megakey1' 2>&1 | head -20")

# Check Flutter
print("=== Checking Flutter ===")
run_cmd("curl -s http://localhost:42002/flutter/ 2>&1 | head -30")

client.close()
print("\n=== Done ===")
