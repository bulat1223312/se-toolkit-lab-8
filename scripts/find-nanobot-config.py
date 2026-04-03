#!/usr/bin/env python3
"""Find nanobot config files."""

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
        print(output[-4000:] if len(output) > 4000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Find nanobot config files
print('=== Finding nanobot config files ===')
run_cmd('find /root -name "*.json" -path "*nanobot*" 2>&1 | head -20')

# Check workspace config
print('=== Checking workspace config ===')
run_cmd('ls -la /root/se-toolkit-lab-8/nanobot/workspace/ 2>&1')

# Check if there's a channels.json or similar
print('=== Looking for channels config ===')
run_cmd('find /root/se-toolkit-lab-8/nanobot -name "*.json" 2>&1')

# Check home directory for nanobot config
print('=== Checking ~/.nanobot ===')
run_cmd('ls -la ~/.nanobot/ 2>&1')

client.close()
print('\n=== Done ===')
