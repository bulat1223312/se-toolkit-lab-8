#!/usr/bin/env python3
"""Check webchat entry points."""

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

# Check entry points
print('=== Checking entry points ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 python -c "import importlib.metadata; eps = importlib.metadata.entry_points(); webchat_eps = [ep for ep in eps if \'webchat\' in ep.name or \'webchat\' in str(ep.group)]; print(webchat_eps)" 2>&1')

# Check nanobot channel registry
print('=== Nanobot channel registry ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 python -c "from nanobot.channels.registry import ChannelRegistry; print(ChannelRegistry.discover_all())" 2>&1')

# Check pip show nanobot-webchat
print('=== pip show nanobot-webchat ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip show nanobot-webchat 2>&1')

# Check nanobot-webchat pyproject.toml
print('=== nanobot-webchat pyproject.toml ===')
run_cmd('cat /app/nanobot-websocket-channel/nanobot-webchat/pyproject.toml 2>&1')

client.close()
print('\n=== Done ===')
