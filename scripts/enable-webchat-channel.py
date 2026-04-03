#!/usr/bin/env python3
"""Enable webchat channel."""

import paramiko

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
        print(output[-4000:] if len(output) > 4000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Check channels login help
print('=== nanobot channels login --help ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot channels login --help 2>&1')

# Try to enable webchat
print('=== nanobot channels login webchat ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 echo "megakey1" | nanobot channels login webchat 2>&1')

# Check status
print('=== nanobot channels status ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot channels status 2>&1')

client.close()
print('\n=== Done ===')
