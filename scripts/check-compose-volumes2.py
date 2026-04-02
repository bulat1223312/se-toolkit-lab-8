#!/usr/bin/env python3
"""Check docker-compose.yml volumes."""

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

# Check docker-compose.yml nanobot section
print('=== docker-compose.yml nanobot section ===')
run_cmd('sed -n "/^  nanobot:/,/^  [a-z]/p" /root/se-toolkit-lab-8/docker-compose.yml | head -50')

# Check if directory exists on host
print('=== Host directory ===')
run_cmd('ls -la /root/se-toolkit-lab-8/nanobot-websocket-channel/ 2>&1')

client.close()
print('\n=== Done ===')
