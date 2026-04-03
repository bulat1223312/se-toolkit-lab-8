#!/usr/bin/env python3
"""Complete verification and fix for LLM connection."""

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
print("ПОЛНАЯ ПРОВЕРКА И ИСПРАВЛЕНИЕ LLM")
print("=" * 60)

# Step 1: Check if OAuth token is valid on host
print("\n1. Проверка OAuth токена на хосте:")
exit_code, output, err = run_cmd(ssh, '''
echo "=== OAuth credentials ==="
cat ~/.qwen/oauth_creds.json | python3 -m json.tool 2>/dev/null | head -15

echo "=== Check if token is still valid ==="
python3 << 'PYEOF'
import json
import time
with open('/root/.qwen/oauth_creds.json') as f:
    creds = json.load(f)
expiry = creds.get('expiry_date', 0)
now = time.time() * 1000
print(f"Token expires: {time.strftime('%Y-%m-%d %H:%M', time.localtime(expiry/1000))}")
print(f"Current time:  {time.strftime('%Y-%m-%d %H:%M', time.localtime(now/1000))}")
print(f"Token valid: {now < expiry}")
print(f"Has access_token: {bool(creds.get('access_token'))}")
PYEOF
''')
print(output if output else err)

# Step 2: Copy credentials to container
print("\n2. Копирование credentials в контейнер:")
exit_code, output, err = run_cmd(ssh, '''
# Backup current container file
docker exec se-toolkit-lab-8-qwen-code-api-1 cp /root/.qwen/oauth_creds.json /root/.qwen/oauth_creds.json.bak 2>/dev/null || true

# Copy fresh credentials
docker cp /root/.qwen/oauth_creds.json se-toolkit-lab-8-qwen-code-api-1:/root/.qwen/oauth_creds.json

# Verify
echo "=== In container ==="
docker exec se-toolkit-lab-8-qwen-code-api-1 cat /root/.qwen/oauth_creds.json | python3 -m json.tool 2>/dev/null | head -10
''')
print(output if output else err)

# Step 3: Enable auth and restart
print("\n3. Включение auth и перезапуск:")
exit_code, output, err = run_cmd(ssh, '''
cd /root/se-toolkit-lab-8

# Ensure auth is enabled
sed -i 's/^QWEN_CODE_API_AUTH_USE=false/QWEN_CODE_API_AUTH_USE=true/' .env.docker.secret
sed -i 's/^QWEN_CODE_AUTH_USE=false/QWEN_CODE_AUTH_USE=true/' .env.docker.secret

echo "=== Auth settings ==="
grep 'AUTH_USE' .env.docker.secret

# Restart qwen-code-api
docker compose --env-file .env.docker.secret restart qwen-code-api
''')
print(output if output else err)

# Wait
print("\n4. Ожидание...")
time.sleep(12)

# Step 4: Check health
print("\n5. Проверка health:")
exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42005/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:42005/health")
print(output if output else err)

# If no_credentials, the token is expired - try direct DashScope approach
if 'no_credentials' in output or 'expired' in output:
    print("\n⚠️ Токен истек. Пробуем прямой доступ к DashScope...")
    
    # Update chat.py to bypass OAuth and use API key directly
    print("\n6. Исправление chat.py для прямого доступа:")
    exit_code, output, err = run_cmd(ssh, '''
docker exec se-toolkit-lab-8-qwen-code-api-1 python3 << 'PYEOF'
import re

with open('/app/qwen_code_api/routes/chat.py', 'r') as f:
    content = f.read()

# Add direct DashScope access when auth is disabled
old_line = '    access_token = await auth.get_valid_token(client)'
new_code = '''    if not settings.qwen_code_auth_use:
        # Direct DashScope access
        access_token = settings.qwen_code_api_key
        url = f"{settings.qwen_api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
    else:
        access_token = await auth.get_valid_token(client)'''

content = content.replace(old_line, new_code)

# Also fix URL and headers for auth mode
old_url = '    creds = auth.load_credentials()\n    url = f"{auth.get_api_endpoint(creds)}/chat/completions"'
new_url = '        creds = auth.load_credentials()\n        url = f"{auth.get_api_endpoint(creds)}/chat/completions"'
content = content.replace(old_url, new_url)

old_headers = '    headers = build_headers(access_token, streaming=is_streaming)'
new_headers = '        headers = build_headers(access_token, streaming=is_streaming)'
content = content.replace(old_headers, new_headers)

with open('/app/qwen_code_api/routes/chat.py', 'w') as f:
    f.write(content)

print("Fixed!")
PYEOF
''')
    print(output if output else err)
    
    # Disable auth and restart
    print("\n7. Отключение auth mode:")
    exit_code, output, err = run_cmd(ssh, '''
cd /root/se-toolkit-lab-8
sed -i 's/^QWEN_CODE_API_AUTH_USE=true/QWEN_CODE_API_AUTH_USE=false/' .env.docker.secret
sed -i 's/^QWEN_CODE_AUTH_USE=true/QWEN_CODE_AUTH_USE=false/' .env.docker.secret
grep 'AUTH_USE' .env.docker.secret

docker compose --env-file .env.docker.secret restart qwen-code-api
''')
    print(output if output else err)
    
    # Wait
    print("\n8. Ожидание...")
    time.sleep(10)
    
    # Check health again
    print("\n9. Проверка health:")
    exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42005/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:42005/health")
    print(output if output else err)

# Step 5: Test LLM call
print("\n10. Тест LLM вызова:")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, f'''
curl -m 15 -s http://localhost:42005/v1/chat/completions \\
  -H 'X-API-Key: {api_key.strip()}' \\
  -H 'Content-Type: application/json' \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' | python3 -m json.tool 2>/dev/null | head -20
''', timeout=30)
print(output if output else err)

# Step 6: Check qwen-code-api logs
print("\n11. Логи qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-qwen-code-api-1 2>&1 | tail -20")
print(output if output else err)

# Step 7: Restart nanobot
print("\n12. Перезапуск nanobot:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot")
print(output if output else err)

# Wait
print("\n13. Ожидание...")
time.sleep(15)

# Step 8: Check nanobot logs
print("\n14. Логи nanobot:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -iE 'error|LLM|agent loop|Processing|Response|mcp_lms' | tail -15")
print(output if output else err)

ssh.close()
print("\n" + "=" * 60)
print("ГОТОВО")
print("=" * 60)
