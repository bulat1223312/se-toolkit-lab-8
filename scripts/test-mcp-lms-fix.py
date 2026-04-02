#!/usr/bin/env python3
"""Upload config.json with mcp_lms fix and test."""

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
with open(r"c:\Users\user\se-toolkit-lab-8\nanobot\config.json", "rb") as f:
    content = f.read()

# Encode as base64
encoded = base64.b64encode(content).decode()

# Decode and write on VM
print("=== Writing config.json ===")
stdin, stdout, stderr = client.exec_command(f'echo "{encoded}" | base64 -d > /root/se-toolkit-lab-8/nanobot/config.json')
err = stderr.read().decode()
print(f"ERR: {err}" if err else "Success!")

# Verify
print("=== Verifying ===")
run_cmd('grep mcp_lms /root/se-toolkit-lab-8/nanobot/config.json')

# Restart nanobot
print("=== Restarting nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot")

# Wait
print("Waiting 30 seconds...")
time.sleep(30)

# Check logs
print("=== Logs ===")
run_cmd("docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -80")

# Test WebSocket
print("=== Testing WebSocket ===")
run_cmd("curl -s -i 'http://localhost:42002/ws/chat?access_key=megakey1' 2>&1 | head -20")

# Check Flutter
print("=== Checking Flutter ===")
run_cmd("curl -s http://localhost:42002/flutter/ 2>&1 | head -30")

client.close()
print("\n=== Done ===")
