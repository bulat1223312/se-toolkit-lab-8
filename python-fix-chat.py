#!/usr/bin/env python3
"""Use Python to fix chat.py in container."""

import paramiko

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
print("ИСПРАВЛЕНИЕ CHAT.PY ЧЕРЕЗ PYTHON")
print("=" * 60)

# Use Python to edit the file in container
print("\n1. Исправление через Python:")
exit_code, output, err = run_cmd(ssh, '''
docker exec se-toolkit-lab-8-qwen-code-api-1 python3 << 'PYEOF'
import re

# Read the file
with open('/app/qwen_code_api/routes/chat.py', 'r') as f:
    content = f.read()

# Fix 1: Replace auth token line
old_auth = "access_token = await auth.get_valid_token(client)"
new_auth = """if settings.qwen_code_auth_use:
        access_token = await auth.get_valid_token(client)
    else:
        access_token = settings.qwen_code_api_key"""
content = content.replace(old_auth, new_auth)

# Fix 2: Replace URL line
old_url = """creds = auth.load_credentials()
    url = f"{auth.get_api_endpoint(creds)}/chat/completions\""""
new_url = """if settings.qwen_code_auth_use:
        creds = auth.load_credentials()
        url = f"{auth.get_api_endpoint(creds)}/chat/completions"
    else:
        url = f"{settings.qwen_api_base}/chat/completions\""""
content = content.replace(old_url, new_url)

# Fix 3: Replace headers line
old_headers = "headers = build_headers(access_token, streaming=is_streaming)"
new_headers = """if settings.qwen_code_auth_use:
        headers = build_headers(access_token, streaming=is_streaming)
    else:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        if is_streaming:
            headers["Accept"] = "text/event-stream\""""
content = content.replace(old_headers, new_headers)

# Write back
with open('/app/qwen_code_api/routes/chat.py', 'w') as f:
    f.write(content)

print("✅ File fixed")
PYEOF
''')
print(output if output else err)

# Verify
print("\n2. Проверка:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 grep -n 'qwen_code_auth_use' /app/qwen_code_api/routes/chat.py")
print(output if output else err)

# Restart
print("\n3. Перезапуск:")
exit_code, output, err = run_cmd(ssh, "docker restart se-toolkit-lab-8-qwen-code-api-1")
print(output if output else err)

# Wait
print("\n4. Ожидание...")
run_cmd(ssh, "sleep 8")

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

# Logs
print("\n6. Логи:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-qwen-code-api-1 2>&1 | tail -10")
print(output if output else err)

ssh.close()
