#!/usr/bin/env python3
"""Check and fix access key."""

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
    if output:
        print(output[-2000:] if len(output) > 2000 else output)
    return output

# Check what access key is configured
print('=== Checking .env.docker.secret ===')
run_cmd('grep NANOBOT_ACCESS_KEY /root/se-toolkit-lab-8/.env.docker.secret 2>&1')

# Check docker-compose.yml for nanobot service
print('=== Checking docker-compose.yml nanobot env ===')
run_cmd('grep -A 25 "nanobot:" /root/se-toolkit-lab-8/docker-compose.yml | grep -E "NANOBOT|access"')

# Check config.resolved.json
print('=== Checking config.resolved.json webchat ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json | grep -A 10 webchat')

# Check entrypoint.py for access key handling
print('=== Checking entrypoint.py for access key ===')
run_cmd('grep -A 5 "access_key" /root/se-toolkit-lab-8/nanobot/entrypoint.py')

client.close()
print('\n=== Done ===')
