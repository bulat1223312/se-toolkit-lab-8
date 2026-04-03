#!/usr/bin/env python3
"""Fix qwen-code-api indentation error."""

import paramiko

VM_HOST = "10.93.25.49"
VM_USER = "root"
VM_PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VM_HOST, username=VM_USER, password=VM_PASSWORD, timeout=30,
               allow_agent=False, look_for_keys=False)

# Check the problematic file
stdin, stdout, stderr = client.exec_command("sed -n '105,120p' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py")
print("Lines 105-120:")
print(stdout.read().decode())

# Fix indentation - remove extra spaces
client.exec_command("""sed -i 's/^        headers = build_headers/    headers = build_headers/' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py""")

# Verify fix
stdin, stdout, stderr = client.exec_command("sed -n '105,120p' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py")
print("\nAfter fix:")
print(stdout.read().decode())

# Rebuild and restart
stdin, stdout, stderr = client.exec_command(
    "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build qwen-code-api 2>&1 | tail -20",
    timeout=180
)
print("\nRebuild output:")
print(stdout.read().decode())

stdin, stdout, stderr = client.exec_command(
    "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d qwen-code-api 2>&1",
    timeout=60
)
print("\nRestart output:")
print(stdout.read().decode())

# Wait and check
import time
time.sleep(5)

stdin, stdout, stderr = client.exec_command(
    "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps qwen-code-api"
)
print("\nStatus:")
print(stdout.read().decode())

stdin, stdout, stderr = client.exec_command(
    "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api --tail 20"
)
print("\nLogs:")
print(stdout.read().decode())

# Test health
stdin, stdout, stderr = client.exec_command("curl -s http://localhost:42005/health")
print("\nHealth check:")
print(stdout.read().decode())

client.close()
