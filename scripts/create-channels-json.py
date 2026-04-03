#!/usr/bin/env python3
"""Create channels.json and test."""

import paramiko
import json
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
        print(output[-2000:] if len(output) > 2000 else output)
    if err:
        print(f"ERR: {err[-500:]}")
    return output, err

# Create channels.json in workspace
channels_config = {
    'channels': {
        'webchat': {
            'enabled': True,
            'host': '0.0.0.0',
            'port': 8765
        }
    }
}

print('=== Creating channels.json ===')
run_cmd(f'echo \'{json.dumps(channels_config)}\' > /root/se-toolkit-lab-8/nanobot/workspace/channels.json')

# Also try creating in ~/.nanobot
print('=== Creating ~/.nanobot/channels.json ===')
run_cmd(f'echo \'{json.dumps(channels_config)}\' > ~/.nanobot/channels.json')

# Check files
print('=== Checking files ===')
run_cmd('cat /root/se-toolkit-lab-8/nanobot/workspace/channels.json 2>&1')
run_cmd('cat ~/.nanobot/channels.json 2>&1')

# Restart nanobot
print('=== Restarting nanobot ===')
run_cmd('docker restart se-toolkit-lab-8-nanobot-1 2>&1')

# Wait
print('Waiting 15 seconds...')
time.sleep(15)

# Check logs
print('=== Logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -E "channel|Channel|webchat|WebChat" | tail -20')

# Check channels status
print('=== Channels status ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot channels status 2>&1')

# Test WebSocket
print('=== WebSocket test ===')
run_cmd("curl -s -i 'http://localhost:42002/ws/chat?access_key=megakey1' 2>&1 | head -15")

client.close()
print('\n=== Done ===')
