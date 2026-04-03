#!/usr/bin/env python3
"""Upload and verify REPORT.md."""

import paramiko
import base64

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
        print(f"ERR: {err[-500:]}")
    return output, err

# Read local REPORT.md
with open(r"c:\Users\user\se-toolkit-lab-8\REPORT.md", "rb") as f:
    content = f.read()

# Encode and upload
encoded = base64.b64encode(content).decode()
print("=== Uploading REPORT.md ===")
stdin, stdout, stderr = client.exec_command(f'echo "{encoded}" | base64 -d > /root/se-toolkit-lab-8/REPORT.md')
err = stderr.read().decode()
print(f'Done' if not err else f'ERR: {err}')

# Verify
print("=== Verifying PASS count ===")
run_cmd('grep -c PASS /root/se-toolkit-lab-8/REPORT.md')

# Show Task 2A section
print("=== Task 2A section ===")
run_cmd('sed -n "/## Task 2A/,/## Task 2B/p" /root/se-toolkit-lab-8/REPORT.md | head -20')

# Show Task 2B section
print("=== Task 2B section ===")
run_cmd('sed -n "/## Task 2B/,/## Task 3/p" /root/se-toolkit-lab-8/REPORT.md | head -20')

client.close()
print('\n=== Done ===')
