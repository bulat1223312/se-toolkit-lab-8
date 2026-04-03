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
    stdin, stdout, stderr = client.exec_command(command, timeout=30)
    output = stdout.read().decode('utf-8', errors='replace')
    if output:
        print(output.strip()[-2000:] if len(output) > 2000 else output.strip())
    return output

# Upload REPORT.md
print('=== Uploading REPORT.md ===')
import base64
with open(r'c:\Users\user\se-toolkit-lab-8\REPORT.md', 'rb') as f:
    content = f.read()
encoded = base64.b64encode(content).decode()
stdin, stdout, stderr = client.exec_command(f'echo "{encoded}" | base64 -d > /root/se-toolkit-lab-8/REPORT.md')
print('Done' if not stderr.read().decode() else 'Failed')

# Verify
print('\n=== PASS count ===')
run_cmd('grep -c PASS /root/se-toolkit-lab-8/REPORT.md')

print('\n=== Status lines ===')
run_cmd('grep "Status:" /root/se-toolkit-lab-8/REPORT.md')

print('\n=== MCP connected ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -c "MCP server.*connected"')

print('\n=== Flutter ===')
run_cmd('curl -s http://localhost:42002/flutter/ | grep -c "Nanobot"')

print('\n=== pyproject.toml ===')
run_cmd('cat /root/se-toolkit-lab-8/nanobot/pyproject.toml')

client.close()
print('\n=== DONE ===')
