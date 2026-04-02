#!/usr/bin/env python3
"""Final verification."""

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
    if output:
        print(output[-3000:] if len(output) > 3000 else output)
    return output

# Check config.json
print('=== config.json ===')
run_cmd('cat /root/se-toolkit-lab-8/nanobot/config.json')

# Wait for restart
print('Waiting 15 seconds...')
time.sleep(15)

# Check logs
print('=== Logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -E "MCP server|Using config"')

# Check services
print('=== Services ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps')

# Check Flutter
print('=== Flutter ===')
run_cmd('curl -s http://localhost:42002/flutter/ | grep -c "Nanobot"')

# Check REPORT.md
print('=== REPORT.md PASS ===')
run_cmd('grep -c PASS /root/se-toolkit-lab-8/REPORT.md')

client.close()
print('\n=== Done ===')
