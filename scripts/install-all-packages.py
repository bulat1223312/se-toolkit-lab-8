#!/usr/bin/env python3
"""Install all required packages in nanobot container."""

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
        print(output[-3000:] if len(output) > 3000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Stop nanobot first
print('=== Stopping nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop nanobot')

# Install packages in order
print('=== Installing nanobot-channel-protocol ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip install -e /app/nanobot-websocket-channel/nanobot-channel-protocol 2>&1')

print('=== Installing lms-mcp ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip install -e /app/mcp 2>&1')

print('=== Installing mcp-webchat ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip install -e /app/nanobot-websocket-channel/mcp-webchat 2>&1')

print('=== Installing nanobot-webchat ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip install -e /app/nanobot-websocket-channel/nanobot-webchat 2>&1')

# Verify installations
print('=== Verifying installations ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip list | grep -E "lms|mcp|nanobot" 2>&1')

# Start nanobot
print('=== Starting nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot')

# Wait
time.sleep(10)

# Check logs
print('=== Nanobot logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -60')

# Test WebSocket
print('=== Testing WebSocket ===')
run_cmd('curl -s -i http://localhost:42002/ws/chat 2>&1 | head -10')

# Check Flutter
print('=== Checking Flutter ===')
run_cmd('curl -s http://localhost:42002/flutter/ | head -20')

client.close()
print('\n=== Done ===')
