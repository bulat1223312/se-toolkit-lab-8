#!/usr/bin/env python3
"""Check mcp package structure."""

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

# Check mcp package structure
print('=== mcp package structure ===')
run_cmd('ls -la /app/mcp/')

print('=== mcp_lms structure ===')
run_cmd('ls -la /app/mcp/mcp_lms/')

print('=== mcp pyproject.toml ===')
run_cmd('cat /app/mcp/pyproject.toml')

# Check if lms_mcp exists anywhere
print('=== Finding lms_mcp ===')
run_cmd('find /app -name "*lms_mcp*" 2>&1')

# Check pip show lms-mcp
print('=== pip show lms-mcp ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip show lms-mcp 2>&1')

client.close()
print('\n=== Done ===')
