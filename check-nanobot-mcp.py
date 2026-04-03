#!/usr/bin/env python3
"""Check and fix nanobot MCP servers."""

import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=30):
    print(f"\n--- {cmd[:70]} ---")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out)
    if err: print(f"STDERR: {err}")
    return out, err

# Check current nanobot status
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps nanobot")

# Check nanobot logs
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail 30")

# Check if MCP packages are installed inside container
run("docker exec se-toolkit-lab-8-nanobot-1 pip list 2>&1 | grep -i mcp")

# Check if webchat channel is available
run("docker exec se-toolkit-lab-8-nanobot-1 pip list 2>&1 | grep -i webchat")

# Check the entrypoint output
run("docker exec se-toolkit-lab-8-nanobot-1 ls -la /app/nanobot-websocket-channel/ 2>&1 | head -10")

# The issue is that MCP servers are not found because they're not in PYTHONPATH
# Let's check the Dockerfile to see how it's set up
run("cat /root/se-toolkit-lab-8/nanobot/Dockerfile")

# Restart nanobot to see fresh logs
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot 2>&1")
time.sleep(10)
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail 50")

client.close()
