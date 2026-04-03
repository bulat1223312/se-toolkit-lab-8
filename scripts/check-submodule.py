#!/usr/bin/env python3
"""Check nanobot-websocket-channel submodule."""

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
        print(output[-2000:] if len(output) > 2000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Check if nanobot-websocket-channel is a submodule
print('=== Checking nanobot-websocket-channel ===')
run_cmd('ls -la /root/se-toolkit-lab-8/nanobot-websocket-channel/.git 2>&1')

# Check git submodule status
print('=== Git submodule status ===')
run_cmd('cd /root/se-toolkit-lab-8 && git submodule status 2>&1')

# Check .gitmodules
print('=== .gitmodules ===')
run_cmd('cat /root/se-toolkit-lab-8/.gitmodules 2>&1')

# Init and update submodules
print('=== Init submodules ===')
run_cmd('cd /root/se-toolkit-lab-8 && git submodule update --init --recursive 2>&1')

# Check again
print('=== After init - submodule status ===')
run_cmd('cd /root/se-toolkit-lab-8 && git submodule status 2>&1')

# Check directory
print('=== nanobot-websocket-channel contents ===')
run_cmd('ls -la /root/se-toolkit-lab-8/nanobot-websocket-channel/')

client.close()
print('\n=== Done ===')
