#!/usr/bin/env python3
"""Wait and check full logs."""

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

# Wait a bit more
print('Waiting 30 seconds...')
time.sleep(30)

# Full logs
print('=== Full logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1')

# Check installed packages
print('=== Installed packages ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip list 2>&1')

# Test WebSocket
print('=== Testing WebSocket ===')
run_cmd('curl -s -i http://localhost:42002/ws/chat 2>&1 | head -10')

# Check Flutter
print('=== Checking Flutter ===')
run_cmd('curl -s http://localhost:42002/flutter/ 2>&1 | head -30')

client.close()
print('\n=== Done ===')
