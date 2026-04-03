#!/usr/bin/env python3
"""Check status after entrypoint update."""

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
    if output:
        print(output[-3000:] if len(output) > 3000 else output)
    return output

# Wait for restart
print('Waiting 15 seconds...')
time.sleep(15)

# Check logs for channels
print('=== Logs (channels) ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -iE "channel|enabled|webchat" | tail -30')

# Check full logs
print('=== Full logs (last 50) ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -50')

# Check config.resolved.json
print('=== config.resolved.json channels ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json | grep -A 15 channels')

# Test WebSocket
print('=== Testing WebSocket ===')
run_cmd("curl -s -i 'http://localhost:42002/ws/chat?access_key=megakey1' 2>&1 | head -20")

# Check if port 8765 is listening
print('=== Checking port 8765 ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /proc/net/tcp 2>&1')

client.close()
print('\n=== Done ===')
