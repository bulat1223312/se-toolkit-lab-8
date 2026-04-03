#!/usr/bin/env python3
"""Refresh token using container's Python environment."""

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
print("ОБНОВЛЕНИЕ ТОКЕНА ЧЕРЕЗ КОНТЕЙНЕР")
print("=" * 60)

# Use container's Python to refresh token
print("\n1. Обновление токена:")
exit_code, output, err = run_cmd(ssh, '''
docker exec se-toolkit-lab-8-qwen-code-api-1 python3 << 'PYEOF'
import json
import httpx
import time
import subprocess

# Load credentials
with open('/root/.qwen/oauth_creds.json') as f:
    creds = json.load(f)

refresh_token = creds.get('refresh_token', '')
client_id = 'f0304373b74a44d2b584a3fb70ca9e56'

print(f"Refresh token: {refresh_token[:20]}...")

try:
    with httpx.Client(timeout=15) as client:
        resp = client.post(
            'https://chat.qwen.ai/api/v1/oauth2/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': client_id,
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
            }
        )
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            new_data = resp.json()
            print(f"New token received!")
            
            # Update credentials
            creds.update(new_data)
            creds['expiry_date'] = int((time.time() + 365 * 24 * 60 * 60) * 1000)
            
            with open('/root/.qwen/oauth_creds.json', 'w') as f:
                json.dump(creds, f, indent=2)
            
            print("✅ Container credentials updated!")
            
            # Copy to host
            subprocess.run([
                'docker', 'cp',
                'se-toolkit-lab-8-qwen-code-api-1:/root/.qwen/oauth_creds.json',
                '/root/.qwen/oauth_creds.json'
            ])
            print("✅ Host credentials updated!")
        else:
            print(f"Error: {resp.status_code}")
            print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")
PYEOF
''', timeout=30)
print(output if output else err)

# Check result
print("\n2. Проверка:")
exit_code, output, err = run_cmd(ssh, "cat /root/.qwen/oauth_creds.json | python3 -m json.tool 2>/dev/null | head -10")
print(output if output else err)

# Restart
print("\n3. Перезапуск:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart qwen-code-api nanobot")
print(output if output else err)

# Wait
print("\n4. Ожидание...")
run_cmd(ssh, "sleep 10")

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
