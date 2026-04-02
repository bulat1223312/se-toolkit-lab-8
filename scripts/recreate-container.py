#!/usr/bin/env python3
"""Recreate nanobot container and verify volumes."""

import paramiko
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

# Stop and remove container
print('=== Stopping and removing container ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret down nanobot')

# Start fresh
print('=== Starting nanobot fresh ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot')

# Wait
print('Waiting 40 seconds...')
time.sleep(40)

# Check volumes in container
print('=== Checking volumes in container ===')
run_cmd('docker inspect se-toolkit-lab-8-nanobot-1 --format="{{json .Mounts}}" 2>&1')

# Check if directories exist
print('=== Checking /app directories ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 ls -la /app/ 2>&1')

# Check logs
print('=== Logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -150')

# Check installed packages
print('=== Installed packages ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip list | grep -E "lms|mcp|nanobot" 2>&1')

# Test WebSocket
print('=== Testing WebSocket ===')
run_cmd("curl -s -i 'http://localhost:42002/ws/chat?access_key=megakey1' 2>&1 | head -15")

client.close()
print('\n=== Done ===')
