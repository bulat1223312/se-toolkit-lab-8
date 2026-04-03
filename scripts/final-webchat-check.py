#!/usr/bin/env python3
"""Final check on webchat channel."""

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
        print(output[-5000:] if len(output) > 5000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Check full logs
print('=== Full logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -100')

# Check if port 18790 is listening (gateway)
print('=== Gateway port 18790 ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /proc/net/tcp 2>&1')

# Check config.resolved.json
print('=== config.resolved.json ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json')

client.close()
print('\n=== Done ===')
