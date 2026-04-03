#!/usr/bin/env python3
"""Fully recreate nanobot container with volumes."""

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
        print(output[-6000:] if len(output) > 6000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Stop and remove container completely
print('=== Stopping and removing container ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret down nanobot && docker rm -f se-toolkit-lab-8-nanobot-1 2>&1')

# Remove image to force rebuild
print('=== Removing image ===')
run_cmd('docker rmi se-toolkit-lab-8-nanobot 2>&1')

# Recreate
print('=== Creating new container ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret create nanobot 2>&1')

# Check mounts before starting
print('=== Checking mounts ===')
run_cmd('docker inspect se-toolkit-lab-8-nanobot-1 --format="{{json .Mounts}}" 2>&1')

# Start
print('=== Starting container ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot 2>&1')

# Wait
print('Waiting 60 seconds...')
time.sleep(60)

# Check logs
print('=== Logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -150')

# Check if modules are installed
print('=== Installed packages ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip list | grep -Ei "lms|mcp|nanobot" 2>&1')

# Check network
print('=== Network connections ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 ss -tlnp 2>&1')

# Test WebSocket
print('=== Testing WebSocket ===')
run_cmd("curl -s -i 'http://localhost:42002/ws/chat?access_key=megakey1' 2>&1 | head -15")

client.close()
print('\n=== Done ===')
