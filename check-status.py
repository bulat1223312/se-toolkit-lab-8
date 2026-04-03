#!/usr/bin/env python3
"""Check service status and logs."""

import paramiko
import sys

VM_HOST = "10.93.25.49"
VM_USER = "root"
VM_PASSWORD = "23112010A.z"
PROJECT = "/root/se-toolkit-lab-8"

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VM_HOST, username=VM_USER, password=VM_PASSWORD, timeout=30,
                   allow_agent=False, look_for_keys=False)
    return client

def run(client, cmd, timeout=30):
    print(f"\n--- {cmd[:70]}{'...' if len(cmd) > 70 else ''} ---")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out)
    if err: print(f"STDERR: {err}")
    return out, err

client = ssh_connect()

# Check qwen-code-api logs
run(client, f"cd {PROJECT} && docker compose --env-file .env.docker.secret logs qwen-code-api --tail 100")

# Check nanobot logs
run(client, f"cd {PROJECT} && docker compose --env-file .env.docker.secret logs nanobot --tail 100")

# Check if websockets is available
run(client, "python3 -c 'import websockets; print(websockets.__version__)' 2>&1")

# Test health endpoint
run(client, "curl -s http://localhost:42005/health 2>&1")

# Check resolved config
run(client, f"cd {PROJECT} && docker exec $(docker compose --env-file .env.docker.secret ps -q nanobot) cat /app/nanobot/config.resolved.json 2>&1")

client.close()
