#!/usr/bin/env python3
"""Check nanobot status after fix."""

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
        print(output[-3000:] if len(output) > 3000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Wait a bit
time.sleep(3)

# Check status
print('=== Container status ===')
run_cmd('docker ps -a | grep nanobot')

# Check logs
print('=== Logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1')

# Check if entrypoint is correct
print('=== Entrypoint first lines ===')
run_cmd('head -20 /root/se-toolkit-lab-8/nanobot/entrypoint.py')

# Check resolved config
print('=== Resolved config ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json 2>&1 || echo "File not found"')

# Check if nanobot is installed
print('=== Nanobot installed? ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 which nanobot')

# Check processes
print('=== Processes in container ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 ps aux 2>&1')

client.close()
print('\n=== Done ===')
