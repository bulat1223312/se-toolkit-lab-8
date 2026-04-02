#!/usr/bin/env python3
"""Debug nanobot volumes and entrypoint."""

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

# Check volumes in container
print('=== Checking mounted volumes ===')
run_cmd('docker inspect se-toolkit-lab-8-nanobot-1 --format="{{range .Mounts}}{{.Source}} -> {{.Destination}}{{\"\n\"}}{{end}}"')

# Check if directories exist in container
print('=== Checking /app/mcp ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 ls -la /app/mcp 2>&1')

print('=== Checking /app/nanobot-websocket-channel ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 ls -la /app/nanobot-websocket-channel 2>&1')

# Check entrypoint execution
print('=== Full logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1')

# Check docker-compose.yml nanobot volumes
print('=== docker-compose.yml nanobot volumes ===')
run_cmd('grep -A 5 "volumes:" /root/se-toolkit-lab-8/docker-compose.yml | head -20')

client.close()
print('\n=== Done ===')
