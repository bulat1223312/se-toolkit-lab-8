#!/usr/bin/env python3
"""Check nanobot container details."""

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
        print(f"ERR: {err}")
    return output, err

# Check nanobot container logs
print('=== Nanobot container logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1')

# Check if nanobot is running
print('=== Nanobot process ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 ps aux')

# Check config
print('=== Config files in container ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 ls -la /app/nanobot/')

# Check entrypoint
print('=== Entrypoint.py ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/entrypoint.py | head -50')

# Check network
print('=== Network connections ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 netstat -tlnp 2>/dev/null || ss -tlnp')

client.close()
print('\n=== Done ===')
