#!/usr/bin/env python3
"""Final rebuild of nanobot."""

import paramiko
import time

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)
sftp = client.open_sftp()

def run_cmd(command, timeout=60, print_out=True):
    if print_out:
        print(f"\n>>> {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if print_out:
        if output:
            print(output[-3000:] if len(output) > 3000 else output)
        if err:
            print(f"ERR: {err[-1000:]}")
    return output, err

# Upload Dockerfile
print("=== Uploading Dockerfile ===")
sftp.put(r"c:\Users\user\se-toolkit-lab-8\nanobot\Dockerfile", "/root/se-toolkit-lab-8/nanobot/Dockerfile")

# Verify
print("=== Dockerfile content ===")
run_cmd("cat /root/se-toolkit-lab-8/nanobot/Dockerfile")

# Stop nanobot
print("\n=== Stopping nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop nanobot")

# Rebuild
print("\n=== Rebuilding nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot 2>&1", timeout=300)

# Start
print("\n=== Starting nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot")

# Wait
print("Waiting 10 seconds...")
time.sleep(10)

# Check logs
print("\n=== Nanobot logs ===")
run_cmd("docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -60")

# Check status
print("\n=== Container status ===")
run_cmd("docker ps -a | grep nanobot")

# Test WebSocket
print("\n=== Testing WebSocket ===")
run_cmd("curl -s -i http://localhost:42002/ws/chat 2>&1 | head -10")

# Check Flutter
print("\n=== Checking Flutter ===")
run_cmd("curl -s http://localhost:42002/flutter/ | head -20")

sftp.close()
client.close()
print("\n=== Done ===")
