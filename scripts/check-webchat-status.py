#!/usr/bin/env python3
"""Check webchat channel status."""

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

# Check if port 8765 is listening
print('=== Checking port 8765 ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /proc/net/tcp 2>&1 | head -20')

# Check nanobot processes
print('=== Nanobot processes ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 ps aux 2>&1')

# Check full logs for channel startup
print('=== Full logs for channel ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -i channel')

client.close()
print('\n=== Done ===')
