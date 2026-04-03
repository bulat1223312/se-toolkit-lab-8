#!/usr/bin/env python3
"""Debug lms_mcp and webchat channel."""

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

# Check lms_mcp module location
print('=== Checking lms_mcp module ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 python -c "import lms_mcp; print(lms_mcp.__file__)" 2>&1')

# Check if webchat channel is configured
print('=== Checking config.resolved.json ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json 2>&1')

# Check if webchat channel is listening
print('=== Checking network connections ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 netstat -tlnp 2>&1 || ss -tlnp')

client.close()
print('\n=== Done ===')
