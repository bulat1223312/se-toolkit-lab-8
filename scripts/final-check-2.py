#!/usr/bin/env python3
"""Final check."""

import paramiko

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

def run_cmd(command):
    stdin, stdout, stderr = client.exec_command(command, timeout=30)
    output = stdout.read().decode('utf-8', errors='replace')
    if output:
        print(output.strip()[-1000:] if len(output) > 1000 else output.strip())
    return output

print('=== PASS count ===')
run_cmd('grep -c PASS /root/se-toolkit-lab-8/REPORT.md')

print('=== Status lines ===')
run_cmd('grep "Status:" /root/se-toolkit-lab-8/REPORT.md')

print('=== MCP connected ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -c "MCP server.*connected"')

print('=== Flutter ===')
run_cmd('curl -s http://localhost:42002/flutter/ | grep -c "Nanobot"')

print('=== Services ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps | grep -E "nanobot|backend|caddy|qwen"')

client.close()
print('\n=== DONE ===')
