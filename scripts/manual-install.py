#!/usr/bin/env python3
"""Manually install packages in nanobot container."""

import paramiko
import time

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

def run_cmd(command, timeout=60):
    print(f"\n>>> {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if output:
        print(output[-3000:] if len(output) > 3000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Check entrypoint.py content
print('=== entrypoint.py install_packages function ===')
run_cmd('sed -n "/def install_packages/,/^def /p" /app/nanobot/entrypoint.py 2>&1')

# Manually install packages in running container
print('=== Manually installing lms-mcp ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip install -e /app/mcp 2>&1')

print('=== Manually installing mcp-webchat ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip install -e /app/nanobot-websocket-channel/mcp-webchat 2>&1')

print('=== Manually installing nanobot-webchat ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip install -e /app/nanobot-websocket-channel/nanobot-webchat 2>&1')

# Check if modules are now available
print('=== Checking lms_mcp ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 python -c "import lms_mcp; print(\'OK\')" 2>&1')

print('=== Checking mcp_webchat ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 python -c "import mcp_webchat; print(\'OK\')" 2>&1')

# Restart nanobot to pick up the installed packages
print('=== Restarting nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot')

time.sleep(10)

# Check logs
print('=== Nanobot logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -60')

# Test WebSocket
print('=== Testing WebSocket ===')
run_cmd('curl -s -i http://localhost:42002/ws/chat 2>&1 | head -10')

client.close()
print('\n=== Done ===')
