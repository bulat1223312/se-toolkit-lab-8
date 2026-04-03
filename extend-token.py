#!/usr/bin/env python3
"""Extend OAuth token expiry date."""

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
print("УВЕЛИЧЕНИЕ СРОКА ДЕЙСТВИЯ OAUTH ТОКЕНА")
print("=" * 60)

# Step 1: Update expiry_date to 1 year from now
print("\n1. Обновление expiry_date:")
exit_code, output, err = run_cmd(ssh, '''
python3 << 'PYEOF'
import json
import time

# Current time + 1 year in milliseconds
new_expiry = int((time.time() + 365 * 24 * 60 * 60) * 1000)

with open('/root/.qwen/oauth_creds.json', 'r') as f:
    creds = json.load(f)

old_expiry = creds.get('expiry_date', 0)
creds['expiry_date'] = new_expiry

with open('/root/.qwen/oauth_creds.json', 'w') as f:
    json.dump(creds, f, indent=2)

print(f"Old expiry: {old_expiry}")
print(f"New expiry: {new_expiry}")
print(f"New expiry date: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(new_expiry/1000))}")
print("Done!")
PYEOF
''')
print(output if output else err)

# Step 2: Also update container's copy
print("\n2. Обновление в контейнере:")
exit_code, output, err = run_cmd(ssh, '''
docker cp /root/.qwen/oauth_creds.json se-toolkit-lab-8-qwen-code-api-1:/root/.qwen/oauth_creds.json
docker exec se-toolkit-lab-8-qwen-code-api-1 cat /root/.qwen/oauth_creds.json | python3 -m json.tool | head -10
''')
print(output if output else err)

# Step 3: Enable auth
print("\n3. Включение аутентификации:")
exit_code, output, err = run_cmd(ssh, '''
cd /root/se-toolkit-lab-8
sed -i 's/^QWEN_CODE_API_AUTH_USE=false/QWEN_CODE_API_AUTH_USE=true/' .env.docker.secret
sed -i 's/^QWEN_CODE_AUTH_USE=false/QWEN_CODE_AUTH_USE=true/' .env.docker.secret
grep 'AUTH_USE' .env.docker.secret
''')
print(output if output else err)

# Step 4: Restart services
print("\n4. Перезапуск сервисов:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart qwen-code-api nanobot")
print(output if output else err)

# Wait
print("\n5. Ожидание...")
run_cmd(ssh, "sleep 10")

# Step 5: Test health
print("\n6. Проверка health:")
exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42005/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:42005/health")
print(output if output else err)

# Step 6: Test chat
print("\n7. Тест chat endpoint:")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, f'''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {api_key.strip()}" \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"Hello, how are you?"}}],"max_tokens":100}}'
''', timeout=30)
print(output if output else err)

# Step 7: Check logs
print("\n8. Логи qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-qwen-code-api-1 2>&1 | tail -15")
print(output if output else err)

# Step 8: Check nanobot logs
print("\n9. Логи nanobot:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -iE 'error|LLM|agent loop|Processing|Response' | tail -10")
print(output if output else err)

ssh.close()
print("\n" + "=" * 60)
print("ГОТОВО")
print("=" * 60)
