#!/usr/bin/env python3
"""Check channels and plugins."""

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

# Check channels status
print('=== nanobot channels status ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot channels status 2>&1')

# Check plugins
print('=== nanobot plugins --help ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot plugins --help 2>&1')

# List plugins
print('=== nanobot plugins list ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot plugins list 2>&1')

# Enable webchat plugin
print('=== nanobot plugins enable webchat ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot plugins enable webchat 2>&1')

# Check channels again
print('=== nanobot channels status after enable ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot channels status 2>&1')

client.close()
print('\n=== Done ===')
