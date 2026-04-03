#!/usr/bin/env python3
"""Rebuild and test nanobot."""

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
        print(output[-4000:] if len(output) > 4000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Verify files
print('=== Verifying pyproject.toml ===')
run_cmd('cat /root/se-toolkit-lab-8/nanobot/pyproject.toml')

# Stop and rebuild
print('\n=== Stopping nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop nanobot')

print('\n=== Rebuilding nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot --no-cache 2>&1', timeout=300)

print('\n=== Starting all services ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d 2>&1', timeout=120)

# Wait for installation
print('\nWaiting 60 seconds for package installation...')
time.sleep(60)

# Check logs
print('\n=== Nanobot logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -100')

# Check status
print('\n=== Service status ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps')

# Test Flutter
print('\n=== Testing Flutter ===')
run_cmd('curl -s http://localhost:42002/flutter/ | head -30')

# Test WebSocket
print('\n=== Testing WebSocket ===')
run_cmd("curl -s -i 'http://localhost:42002/ws/chat?access_key=megakey1' 2>&1 | head -20")

client.close()
print('\n=== Done ===')
