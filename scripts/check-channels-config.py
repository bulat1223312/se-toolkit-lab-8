#!/usr/bin/env python3
"""Check channels configuration."""

import paramiko

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

def run_cmd(command):
    print(f"\n>>> {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=30)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if output:
        print(output[-3000:] if len(output) > 3000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Check config.resolved.json
print('=== config.resolved.json channels ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json | grep -A 5 channels')

# Check full config.resolved.json
print('=== Full config.resolved.json ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json')

# Check entrypoint.py channels section
print('=== entrypoint.py channels ===')
run_cmd('grep -A 10 "webchat" /root/se-toolkit-lab-8/nanobot/entrypoint.py | head -30')

client.close()
print('\n=== Done ===')
