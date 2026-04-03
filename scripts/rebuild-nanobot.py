#!/usr/bin/env python3
"""Fix nanobot pyproject.toml and rebuild."""

import paramiko
import time

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

def run_cmd(command, timeout=60):
    print(f"\n>>> {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if output:
        print(output[-2000:] if len(output) > 2000 else output)
    if err:
        print(f"ERR: {err[-1000:] if len(err) > 1000 else err}")
    return output, err

# Simpler pyproject.toml without workspace deps
pyproject_content = '''[project]
name = "nanobot"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "nanobot-ai>=0.1.0",
    "pydantic-settings>=2.0.0",
]
'''

print("=== Writing new pyproject.toml ===")
stdin, stdout, stderr = client.exec_command("echo '" + pyproject_content.replace("'", "'\"'\"'") + "' > /root/se-toolkit-lab-8/nanobot/pyproject.toml")
print(stdout.read().decode())

# Verify
print("=== Verifying pyproject.toml ===")
run_cmd("cat /root/se-toolkit-lab-8/nanobot/pyproject.toml")

# Rebuild nanobot
print("\n=== Rebuilding nanobot ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot", timeout=300)

# Start services
print("\n=== Starting services ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d", timeout=120)

# Check status
print("\n=== Status ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps")

# Check logs
print("\n=== Nanobot logs ===")
run_cmd("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail=50")

client.close()
print("\n=== Done ===")
