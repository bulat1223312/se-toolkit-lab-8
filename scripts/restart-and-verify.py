#!/usr/bin/env python3
"""Restart nanobot and verify install_packages runs."""

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

# Verify entrypoint has install_packages
print('=== Checking entrypoint.py for install_packages ===')
run_cmd('grep -A 5 "def install_packages" /root/se-toolkit-lab-8/nanobot/entrypoint.py')

# Restart nanobot
print('=== Restarting nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot')

# Wait for package installation
print("Waiting 20 seconds...")
time.sleep(20)

# Check logs
print('=== Nanobot logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -80')

# Check if modules are installed
print('=== Checking installed modules ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip list | grep -E "lms|mcp|nanobot" 2>&1')

# Test WebSocket
print('=== Testing WebSocket ===')
run_cmd('curl -s -i http://localhost:42002/ws/chat 2>&1 | head -10')

client.close()
print('\n=== Done ===')
