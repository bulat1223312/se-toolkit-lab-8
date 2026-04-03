#!/usr/bin/env python3
"""Verify config files on VM."""

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

# Check pyproject.toml
print('=== pyproject.toml ===')
run_cmd('cat /root/se-toolkit-lab-8/nanobot/pyproject.toml')

# Check config.json
print('=== config.json ===')
run_cmd('cat /root/se-toolkit-lab-8/nanobot/config.json')

client.close()
print('\n=== Done ===')
