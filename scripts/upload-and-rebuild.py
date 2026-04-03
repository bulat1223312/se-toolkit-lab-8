#!/usr/bin/env python3
"""Upload files to VM via SFTP and rebuild nanobot."""

import paramiko
import base64

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)
sftp = client.open_sftp()

# Upload entrypoint.py
print("=== Uploading entrypoint.py ===")
sftp.put(r"c:\Users\user\se-toolkit-lab-8\nanobot\entrypoint.py", "/root/se-toolkit-lab-8/nanobot/entrypoint.py")

# Verify
print("=== Verifying ===")
stdin, stdout, stderr = client.exec_command("wc -l /root/se-toolkit-lab-8/nanobot/entrypoint.py")
print(stdout.read().decode())

# Upload config.json
print("=== Uploading config.json ===")
sftp.put(r"c:\Users\user\se-toolkit-lab-8\nanobot\config.json", "/root/se-toolkit-lab-8/nanobot/config.json")

# Rebuild
print("=== Rebuilding nanobot ===")
stdin, stdout, stderr = client.exec_command("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot 2>&1", timeout=300)
output = stdout.read().decode()
print(output[-2000:] if len(output) > 2000 else output)

# Restart
print("=== Restarting nanobot ===")
stdin, stdout, stderr = client.exec_command("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot 2>&1")
print(stdout.read().decode())

import time
time.sleep(5)

# Check logs
print("=== Nanobot logs ===")
stdin, stdout, stderr = client.exec_command("docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -50")
print(stdout.read().decode())

# Check status
print("=== Container status ===")
stdin, stdout, stderr = client.exec_command("docker ps -a | grep nanobot")
print(stdout.read().decode())

sftp.close()
client.close()
print("\n=== Done ===")
