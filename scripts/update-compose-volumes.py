#!/usr/bin/env python3
"""Update docker-compose.yml to add volumes for nanobot."""

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
        print(f"ERR: {err[-1000:]}")
    return output, err

# Read current docker-compose.yml
print('=== Reading docker-compose.yml ===')
stdin, stdout, stderr = client.exec_command('cat /root/se-toolkit-lab-8/docker-compose.yml')
content = stdout.read().decode()

# Find nanobot service and add volumes
# Look for the nanobot service section and add volumes after depends_on
nanobot_section = '''  nanobot:
    build:
      context: ./nanobot
      additional_contexts:
        workspace: .
      args:
        REGISTRY_PREFIX_DOCKER_HUB: ${REGISTRY_PREFIX_DOCKER_HUB:-}
    restart: unless-stopped
    networks:
      - lms-network
    user: "${HOST_UID:-1000}:${HOST_GID:-1000}"
    environment:
      # Task 1 used VM-shell URLs. In Docker, use service-to-service URLs instead.
      - LLM_API_KEY=${LLM_API_KEY:?'LLM_API_KEY is required'}
      - LLM_API_BASE_URL=http://qwen-code-api:${QWEN_CODE_API_CONTAINER_PORT:?'QWEN_CODE_API_CONTAINER_PORT is required'}/v1
      - LLM_API_MODEL=${LLM_API_MODEL:?'LLM_API_MODEL is required'}
      - NANOBOT_LMS_BACKEND_URL=http://backend:${BACKEND_CONTAINER_PORT:?'BACKEND_CONTAINER_PORT is required'}
      - NANOBOT_LMS_API_KEY=${LMS_API_KEY:?'LMS_API_KEY is required'}
      - NANOBOT_GATEWAY_CONTAINER_ADDRESS=${NANOBOT_GATEWAY_CONTAINER_ADDRESS:?'NANOBOT_GATEWAY_CONTAINER_ADDRESS is required'}
      - NANOBOT_GATEWAY_CONTAINER_PORT=${NANOBOT_GATEWAY_CONTAINER_PORT:?'NANOBOT_GATEWAY_CONTAINER_PORT is required'}
      # Task 2B — WebSocket channel settings
      - NANOBOT_WEBCHAT_CONTAINER_ADDRESS=${NANOBOT_WEBCHAT_CONTAINER_ADDRESS:?'NANOBOT_WEBCHAT_CONTAINER_ADDRESS is required'}
      - NANOBOT_WEBCHAT_CONTAINER_PORT=${NANOBOT_WEBCHAT_CONTAINER_PORT:?'NANOBOT_WEBCHAT_CONTAINER_PORT is required'}
      - NANOBOT_ACCESS_KEY=${NANOBOT_ACCESS_KEY:?'NANOBOT_ACCESS_KEY is required'}
    depends_on:
      - backend
      - qwen-code-api
    volumes:
      - ./nanobot:/app/nanobot
      - ./mcp:/app/mcp
      - ./nanobot-websocket-channel:/app/nanobot-websocket-channel
'''

# Replace the nanobot section
import re
old_nanobot = r'  nanobot:\n    build:.*?(?=\n  #|\n  client-web-flutter:|\Z)'
new_content = re.sub(old_nanobot, nanobot_section, content, flags=re.DOTALL)

# Write back
print('=== Writing updated docker-compose.yml ===')
stdin, stdout, stderr = client.exec_command("cat > /root/se-toolkit-lab-8/docker-compose.yml << 'COMPOSE_EOF'\n" + new_content + "\nCOMPOSE_EOF")
print(stdout.read().decode())

# Verify
print('=== Verifying nanobot section ===')
run_cmd('grep -A 40 "  nanobot:" /root/se-toolkit-lab-8/docker-compose.yml | head -45')

# Stop nanobot
print('\n=== Stopping nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop nanobot')

# Rebuild
print('\n=== Rebuilding nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot 2>&1', timeout=300)

# Start
print('\n=== Starting nanobot ===')
run_cmd('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot')

# Wait
print("Waiting 15 seconds for package installation...")
time.sleep(15)

# Check logs
print('\n=== Nanobot logs ===')
run_cmd('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -80')

client.close()
print('\n=== Done ===')
