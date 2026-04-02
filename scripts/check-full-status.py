#!/usr/bin/env python3
"""Check nanobot full status."""

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
        print(output[-5000:] if len(output) > 5000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

time.sleep(3)

# Full logs
print('=== Full logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1')

# Check resolved config
print('=== Resolved config ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json 2>&1')

# Check processes
print('=== Processes ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 ps aux 2>&1')

# Test WebSocket
print('=== Testing WebSocket ===')
run_cmd('curl -s -i http://localhost:42002/ws/chat 2>&1 | head -10')

# Check Flutter
print('=== Checking Flutter ===')
run_cmd('curl -s http://localhost:42002/flutter/ | head -20')

# Check all services
print('=== All services ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps')

client.close()
print('\n=== Done ===')
