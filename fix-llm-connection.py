#!/usr/bin/env python3
"""Fix LLM connection by configuring qwen auth and refreshing token."""

import paramiko
import json

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
print("ИСПРАВЛЕНИЕ LLM ПОДКЛЮЧЕНИЯ")
print("=" * 60)

# Step 1: Update settings.json with auth type
print("\n1. Настройка settings.json с auth type:")
exit_code, output, err = run_cmd(ssh, '''
cat > /root/.qwen/settings.json << 'EOF'
{
  "security": {
    "auth": {
      "type": "qwen-oauth"
    }
  },
  "model": {
    "name": "coder-model"
  },
  "$version": 3
}
EOF
cat /root/.qwen/settings.json
''')
print(output if output else err)

# Step 2: Try to refresh token using the refresh_token endpoint directly
print("\n2. Попытка обновления токена через API:")
exit_code, output, err = run_cmd(ssh, '''
python3 << 'PYEOF'
import json
import urllib.request
import urllib.parse

# Load current credentials
with open('/root/.qwen/oauth_creds.json') as f:
    creds = json.load(f)

refresh_token = creds.get('refresh_token', '')
client_id = 'f0304373b74a44d2b584a3fb70ca9e56'

print(f"Refresh token: {refresh_token[:20]}...")

# Prepare request
data = urllib.parse.urlencode({
    'grant_type': 'refresh_token',
    'refresh_token': refresh_token,
    'client_id': client_id,
}).encode('utf-8')

req = urllib.request.Request(
    'https://chat.qwen.ai/api/v1/oauth2/token',
    data=data,
    headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
    }
)

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        response_data = json.loads(resp.read().decode())
        print(f"Status: {resp.status}")
        print(f"Response: {json.dumps(response_data, indent=2)[:500]}")
        
        if 'access_token' in response_data:
            # Update credentials
            creds.update(response_data)
            with open('/root/.qwen/oauth_creds.json', 'w') as f:
                json.dump(creds, f, indent=2)
            print("✅ Credentials updated successfully!")
        else:
            print("❌ No access_token in response")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Response: {e.read().decode()[:500]}")
except Exception as e:
    print(f"Error: {e}")
PYEOF
''', timeout=30)
print(output if output else err)

# Step 3: Check if token was updated
print("\n3. Проверка oauth_creds.json:")
exit_code, output, err = run_cmd(ssh, "cat /root/.qwen/oauth_creds.json | python3 -m json.tool 2>/dev/null | head -15 || cat /root/.qwen/oauth_creds.json")
print(output if output else err)

# Step 4: Restart qwen-code-api
print("\n4. Перезапуск qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart qwen-code-api")
print(output if output else err)

# Wait
print("\n5. Ожидание...")
run_cmd(ssh, "sleep 8")

# Step 5: Test qwen-code-api health
print("\n6. Проверка health endpoint:")
exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42005/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:42005/health")
print(output if output else err)

# Step 6: Test chat endpoint
print("\n7. Тест chat endpoint:")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, f'''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {api_key.strip()}" \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"Say hello in one sentence"}}],"max_tokens":50}}'
''', timeout=30)
print(output if output else err)

# Step 7: Restart nanobot
print("\n8. Перезапуск nanobot:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot")
print(output if output else err)

# Wait
print("\n9. Ожидание...")
run_cmd(ssh, "sleep 10")

# Step 8: Check nanobot logs
print("\n10. Логи nanobot (последние 15 строк):")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -15")
print(output if output else err)

ssh.close()
print("\n" + "=" * 60)
print("ГОТОВО")
print("=" * 60)
