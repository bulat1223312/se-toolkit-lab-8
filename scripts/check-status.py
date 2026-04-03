#!/usr/bin/env python3
"""Check service status."""

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

# Wait
print('Waiting 30 seconds...')
time.sleep(30)

# Check status
print('=== Service status ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps')

# Check logs
print('=== Nanobot logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -80')

# Test Flutter
print('=== Testing Flutter ===')
run_cmd('curl -s http://localhost:42002/flutter/ | head -30')

# Test WebSocket
print('=== Testing WebSocket ===')
run_cmd("curl -s -i 'http://localhost:42002/ws/chat?access_key=megakey1' 2>&1 | head -20")

client.close()
print('\n=== Done ===')
