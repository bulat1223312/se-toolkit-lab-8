#!/usr/bin/env python3
"""Final verification."""

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

# Check services
print('=== Service status ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps')

# Check Flutter
print('=== Flutter test ===')
run_cmd('curl -s http://localhost:42002/flutter/ | grep -c "Nanobot"')

# Check MCP status
print('=== MCP status ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -E "MCP server.*connected"')

# Check REPORT.md
print('=== REPORT.md PASS count ===')
run_cmd('grep -c PASS /root/se-toolkit-lab-8/REPORT.md')

client.close()
print('\n=== Done ===')
