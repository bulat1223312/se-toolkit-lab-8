#!/usr/bin/env python3
"""Restore backup and apply fix properly."""

import paramiko
import time

VM_HOST = '10.93.25.49'
VM_USER = 'root'
VM_PASSWORD = '23112010A.z'

def run_cmd(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    return exit_code, output, err

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VM_HOST, username=VM_USER, password=VM_PASSWORD, timeout=60)

print("=" * 60)
print("ВОССТАНОВЛЕНИЕ И ИСПРАВЛЕНИЕ")
print("=" * 60)

# Stop container first
print("\n1. Остановка контейнера:")
exit_code, output, err = run_cmd(ssh, "docker stop se-toolkit-lab-8-qwen-code-api-1")
print(output if output else err)

# Restore backup
print("\n2. Восстановление бэкапа:")
exit_code, output, err = run_cmd(ssh, """
# Create a temp script to fix the file
cat > /tmp/fix_chat.py << 'PYEOF'
import re

# Read the backup file
with open('/app/qwen_code_api/routes/chat.py.bak', 'r') as f:
    content = f.read()

# Fix 1: Replace auth token line
old = "    access_token = await auth.get_valid_token(client)"
new = """    if settings.qwen_code_auth_use:
        access_token = await auth.get_valid_token(client)
    else:
        access_token = settings.qwen_code_api_key"""
content = content.replace(old, new)

# Fix 2: Replace URL and creds lines
old = """    creds = auth.load_credentials()
    url = f"{auth.get_api_endpoint(creds)}/chat/completions\""""
new = """    if settings.qwen_code_auth_use:
        creds = auth.load_credentials()
        url = f"{auth.get_api_endpoint(creds)}/chat/completions"
    else:
        url = f"{settings.qwen_api_base}/chat/completions\""""
content = content.replace(old, new)

# Fix 3: Replace headers line
old = "    headers = build_headers(access_token, streaming=is_streaming)"
new = """    if settings.qwen_code_auth_use:
        headers = build_headers(access_token, streaming=is_streaming)
    else:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        if is_streaming:
            headers["Accept"] = "text/event-stream\""""
content = content.replace(old, new)

# Write back
with open('/app/qwen_code_api/routes/chat.py', 'w') as f:
    f.write(content)

print("Fixed!")
PYEOF

# Copy script to container
docker cp /tmp/fix_chat.py se-toolkit-lab-8-qwen-code-api-1:/tmp/fix_chat.py

# Run it
docker start se-toolkit-lab-8-qwen-code-api-1
sleep 2
docker exec se-toolkit-lab-8-qwen-code-api-1 python3 /tmp/fix_chat.py
""")
print(output if output else err)

# Wait for container to stabilize
print("\n3. Ожидание...")
time.sleep(10)

# Check if running
print("\n4. Статус:")
exit_code, output, err = run_cmd(ssh, "docker ps | grep qwen")
print(output if output else err)

# Test
print("\n5. Тест:")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, f'''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {api_key.strip()}" \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"Hello"}}],"max_tokens":50}}'
''', timeout=30)
print(output if output else err)

ssh.close()
