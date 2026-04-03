#!/usr/bin/env python3
"""Rebuild nanobot with MCP servers."""

import paramiko
import time

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)
sftp = client.open_sftp()

def run_cmd(command, timeout=60):
    print(f"\n>>> {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if output:
        print(output[-2000:] if len(output) > 2000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# Upload Dockerfile
print("=== Uploading Dockerfile ===")
sftp.put(r"c:\Users\user\se-toolkit-lab-8\nanobot\Dockerfile", "/root/se-toolkit-lab-8/nanobot/Dockerfile")

# Verify
print("=== Verifying Dockerfile ===")
run_cmd("cat /root/se-toolkit-lab-8/nanobot/Dockerfile")

# Stop nanobot
print("\n=== Stopping nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop nanobot")

# Rebuild
print("\n=== Rebuilding nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot --no-cache", timeout=300)

# Start
print("\n=== Starting nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot")

# Wait
time.sleep(10)

# Check logs
print("\n=== Nanobot logs ===")
run_cmd("docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -50")

# Check status
print("\n=== Container status ===")
run_cmd("docker ps -a | grep nanobot")

sftp.close()
client.close()
print("\n=== Done ===")
