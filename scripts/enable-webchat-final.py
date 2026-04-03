#!/usr/bin/env python3
"""Enable webchat channel."""

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
        print(output[-2000:] if len(output) > 2000 else output)
    return output

# Try to enable webchat channel via login
print('=== Enabling webchat channel ===')
run_cmd('docker exec -i se-toolkit-lab-8-nanobot-1 nanobot channels login webchat 2>&1')

# Wait
time.sleep(3)

# Check channels status
print('=== Channels status ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot channels status 2>&1')

# Restart nanobot
print('=== Restarting nanobot ===')
run_cmd('docker restart se-toolkit-lab-8-nanobot-1 2>&1')

# Wait
time.sleep(10)

# Check logs
print('=== Logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -i "channel" | tail -20')

# Test WebSocket
print('=== Testing WebSocket ===')
run_cmd("curl -s -i 'http://localhost:42002/ws/chat?access_key=megakey1' 2>&1 | head -15")

client.close()
print('\n=== Done ===')
