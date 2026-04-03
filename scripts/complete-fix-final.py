#!/usr/bin/env python3
"""Complete fix and verification."""

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
        print(output[-3000:] if len(output) > 3000 else output)
    if err:
        print(f"ERR: {err[-1000:]}")
    return output, err

# 1. Fix pyproject.toml
pyproject = '''[project]
name = "nanobot"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "nanobot-ai>=0.1.0",
    "pydantic-settings>=2.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''

print('=== 1. Writing pyproject.toml ===')
stdin, stdout, stderr = client.exec_command('cat > /root/se-toolkit-lab-8/nanobot/pyproject.toml << EOF\n' + pyproject + '\nEOF')
print('Done')

# 2. Verify
print('=== 2. Verifying pyproject.toml ===')
run_cmd('cat /root/se-toolkit-lab-8/nanobot/pyproject.toml')

# 3. Stop
print('=== 3. Stopping nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop nanobot')

# 4. Remove image
print('=== 4. Removing old image ===')
run_cmd('docker rmi se-toolkit-lab-8-nanobot 2>&1 || true')

# 5. Rebuild
print('=== 5. Rebuilding nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot 2>&1', timeout=300)

# 6. Start
print('=== 6. Starting nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot')

# Wait
print('Waiting 60 seconds...')
time.sleep(60)

# 7. Check logs
print('=== 7. Logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -40')

# 8. MCP
print('=== 8. MCP servers ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep "MCP server.*connected"')

# 9. WebSocket
print('=== 9. WebSocket test ===')
run_cmd("curl -s -i 'http://localhost:42002/ws/chat?access_key=megakey1' 2>&1 | head -20")

# 10. Channels
print('=== 10. Channels status ===')
run_cmd('docker exec se-toolkit-lab-8-nanobot-1 nanobot channels status 2>&1')

# 11. Flutter
print('=== 11. Flutter ===')
run_cmd('curl -s http://localhost:42002/flutter/ | grep -c "Nanobot"')

client.close()
print('\n=== DONE ===')
