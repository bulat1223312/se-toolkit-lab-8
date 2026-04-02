#!/usr/bin/env python3
"""Check lms_mcp editable install."""

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

# Check top_level.txt
print('=== top_level.txt ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /usr/local/lib/python3.12/site-packages/lms_mcp-1.0.0.dist-info/top_level.txt 2>&1')

# Try to import mcp_lms
print('=== Import mcp_lms ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 python -c "import mcp_lms; print(mcp_lms.__file__)" 2>&1')

# Check editable.pth
print('=== editable.pth ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 cat /usr/local/lib/python3.12/site-packages/__editable__.lms_mcp-1.0.0.pth 2>&1')

client.close()
print('\n=== Done ===')
