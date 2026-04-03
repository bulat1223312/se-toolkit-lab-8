#!/usr/bin/env python3
"""Check lms-mcp structure."""

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

# Check lms-mcp structure on host
print('=== Host mcp structure ===')
run_cmd('ls -la /root/se-toolkit-lab-8/mcp/')

print('=== Host mcp_lms ===')
run_cmd('ls -la /root/se-toolkit-lab-8/mcp/mcp_lms/ 2>&1')

print('=== Host mcp pyproject.toml ===')
run_cmd('cat /root/se-toolkit-lab-8/mcp/pyproject.toml 2>&1')

# Check inside container
print('=== Container /app/mcp ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 ls -la /app/mcp/ 2>&1')

# Check pip show
print('=== pip show lms-mcp ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 pip show -f lms-mcp 2>&1')

# Try to import lms_mcp
print('=== Import lms_mcp ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 python -c "import lms_mcp; print(lms_mcp.__file__)" 2>&1')

# Check site-packages
print('=== site-packages lms_mcp ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 ls -la /usr/local/lib/python3.12/site-packages/ | grep lms 2>&1')

client.close()
print('\n=== Done ===')
