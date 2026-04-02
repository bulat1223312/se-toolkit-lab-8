#!/usr/bin/env python3
"""Login to webchat channel and test."""

import paramiko
import time

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

def run_cmd(command, timeout=30):
    print(f"\n>>> {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if output:
        print(output[-4000:] if len(output) > 4000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Try to login to webchat channel
print('=== nanobot channels login webchat --force ===')
run_cmd('docker exec -i se-toolkit-lab-8-nanobot-1 nanobot channels login webchat --force 2>&1')

# Wait
print('Waiting 5 seconds...')
time.sleep(5)

# Check status
print('=== nanobot channels status ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot channels status 2>&1')

# Restart gateway
print('=== Restarting gateway ===')
run_cmd('docker restart se-toolkit-lab-8-nanobot-1 2>&1')

# Wait
print('Waiting 10 seconds...')
time.sleep(10)

# Check logs
print('=== Logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -50')

# Test WebSocket
print('=== Testing WebSocket ===')
run_cmd("curl -s -i 'http://localhost:42002/ws/chat?access_key=megakey1' 2>&1 | head -20")

# Test Flutter
print('=== Testing Flutter ===')
run_cmd('curl -s http://localhost:42002/flutter/ | head -30')

client.close()
print('\n=== Done ===')
