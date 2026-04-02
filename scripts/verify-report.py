#!/usr/bin/env python3
"""Verify REPORT.md upload."""

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
    if output:
        print(output[-2000:] if len(output) > 2000 else output)
    return output

# Verify PASS count
print('=== PASS count ===')
run_cmd('grep -c PASS /root/se-toolkit-lab-8/REPORT.md')

# Verify Status lines
print('=== Status lines ===')
run_cmd('grep "Status:" /root/se-toolkit-lab-8/REPORT.md')

# Verify Task 2A
print('=== Task 2A ===')
run_cmd('sed -n "/## Task 2A/,/## Task 2B/p" /root/se-toolkit-lab-8/REPORT.md | head -20')

# Final service check
print('=== Service check ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps')

# Flutter check
print('=== Flutter check ===')
run_cmd('curl -s http://localhost:42002/flutter/ | grep -c "Nanobot"')

# MCP check
print('=== MCP check ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep "MCP server.*connected"')

client.close()
print('\n=== Done ===')
