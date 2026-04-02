#!/usr/bin/env python3
"""Add nanobot-websocket-channel as submodule and rebuild."""

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

# Remove existing directory and add as submodule
print('=== Removing existing nanobot-websocket-channel ===')
run_cmd('rm -rf /root/se-toolkit-lab-8/nanobot-websocket-channel')

# Add as submodule
print('=== Adding nanobot-websocket-channel as submodule ===')
run_cmd('cd /root/se-toolkit-lab-8 && git submodule add https://github.com/inno-se-toolkit/nanobot-websocket-channel 2>&1')

# Init and update
print('=== Updating submodules ===')
run_cmd('cd /root/se-toolkit-lab-8 && git submodule update --init --recursive 2>&1', timeout=120)

# Check status
print('=== Submodule status ===')
run_cmd('cd /root/se-toolkit-lab-8 && git submodule status 2>&1')

# Check directory
print('=== nanobot-websocket-channel contents ===')
run_cmd('ls -la /root/se-toolkit-lab-8/nanobot-websocket-channel/ 2>&1')

# Now rebuild nanobot
print('=== Stopping nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop nanobot')

print('=== Rebuilding nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot 2>&1', timeout=300)

print('=== Starting nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot')

# Wait
print("Waiting 10 seconds...")
time.sleep(10)

# Check logs
print('=== Nanobot logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -60')

# Check modules
print('=== Checking installed modules ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 python -c "import lms_mcp; print(\"lms_mcp OK\")" 2>&1')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 python -c "import mcp_webchat; print(\"mcp_webchat OK\")" 2>&1')

client.close()
print('\n=== Done ===')
