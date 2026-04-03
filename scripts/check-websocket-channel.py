#!/usr/bin/env python3
"""Check nanobot-websocket-channel structure on VM."""

import paramiko
import time

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

def run_cmd(command, timeout=30):
    print(f"\n>>> {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if output:
        print(output[-3000:] if len(output) > 3000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Wait for container to be running
print('Waiting 15 seconds...')
time.sleep(15)

# Check directory structure
print('=== nanobot-websocket-channel structure ===')
run_cmd('ls -la /app/nanobot-websocket-channel/')

# Check each subdirectory
print('=== mcp-webchat ===')
run_cmd('ls -la /app/nanobot-websocket-channel/mcp-webchat/')

print('=== nanobot-channel-protocol ===')
run_cmd('ls -la /app/nanobot-websocket-channel/nanobot-channel-protocol/')

# Check pyproject.toml
print('=== nanobot-channel-protocol pyproject.toml ===')
run_cmd('cat /app/nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml 2>&1')

# Check mcp-webchat pyproject.toml
print('=== mcp-webchat pyproject.toml ===')
run_cmd('cat /app/nanobot-websocket-channel/mcp-webchat/pyproject.toml 2>&1')

# Check nanobot-webchat pyproject.toml
print('=== nanobot-webchat pyproject.toml ===')
run_cmd('cat /app/nanobot-websocket-channel/nanobot-webchat/pyproject.toml 2>&1')

client.close()
print('\n=== Done ===')
