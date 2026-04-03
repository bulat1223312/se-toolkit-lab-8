#!/usr/bin/env python3
"""Check nanobot CLI."""

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

# Check nanobot gateway help
print('=== nanobot gateway --help ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot gateway --help 2>&1')

# Check nanobot --help
print('=== nanobot --help ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot --help 2>&1')

# Check nanobot channels enable
print('=== nanobot channels --help ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot channels --help 2>&1')

client.close()
print('\n=== Done ===')
