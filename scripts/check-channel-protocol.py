#!/usr/bin/env python3
"""Check nanobot-channel-protocol requirements."""

import paramiko

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

# Check nanobot-channel-protocol pyproject.toml
print('=== nanobot-channel-protocol pyproject.toml ===')
stdin, stdout, stderr = client.exec_command('cat /app/nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml 2>&1')
print(stdout.read().decode())

# Check if we can install without python version constraint
print('=== Trying to install with --ignore-requires-python ===')
stdin, stdout, stderr = client.exec_command('docker exec se-toolkit-lab-8-nanobot-1 pip install -e /app/nanobot-websocket-channel/nanobot-channel-protocol --ignore-requires-python 2>&1')
print(stdout.read().decode())

client.close()
print('\n=== Done ===')
