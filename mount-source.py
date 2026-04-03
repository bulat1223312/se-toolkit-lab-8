#!/usr/bin/env python3
"""Mount qwen-code-api source code to avoid rebuilding image."""

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
print("МОНТИРОВАНИЕ ИСХОДНОГО КОДА QWEN-CODE-API")
print("=" * 60)

# Read current docker-compose.yml qwen-code-api section
print("\n1. Текущая конфигурация qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "sed -n '/^  qwen-code-api:/,/^  [a-z]/p' /root/se-toolkit-lab-8/docker-compose.yml | head -35")
print(output if output else err)

# Update docker-compose.yml to mount source code
print("\n2. Обновление docker-compose.yml:")
exit_code, output, err = run_cmd(ssh, '''
cd /root/se-toolkit-lab-8

# Backup
cp docker-compose.yml docker-compose.yml.bak

# Use sed to add volume mount for qwen-code-api source
# Find the line with "volumes:" under qwen-code-api and add the mount
python3 << 'PYEOF'
import re

with open('docker-compose.yml', 'r') as f:
    content = f.read()

# Find qwen-code-api section and add volume mount
# Look for the volumes section under qwen-code-api
pattern = r'(  qwen-code-api:.*?volumes:\s*\n\s*- ~/.qwen:/root/.qwen:ro)'
replacement = r'\1\n      - ./qwen-code-api/src:/app/qwen_code_api:ro'

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('docker-compose.yml', 'w') as f:
    f.write(new_content)

print("✅ docker-compose.yml updated")
PYEOF

# Verify
grep -A 3 'volumes:' /root/se-toolkit-lab-8/docker-compose.yml | grep -A 2 'qwen'
''')
print(output if output else err)

# Recreate qwen-code-api
print("\n3. Пересоздание qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret down qwen-code-api && docker compose --env-file .env.docker.secret up -d qwen-code-api")
print(output if output else err)

# Wait
print("\n4. Ожидание...")
run_cmd(ssh, "sleep 10")

# Check if source is mounted
print("\n5. Проверка монтирования:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 ls -la /app/qwen_code_api/routes/chat.py")
print(output if output else err)

# Check if the fix is applied
print("\n6. Проверка исправления:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 grep -A 3 'qwen_code_auth_use' /app/qwen_code_api/routes/chat.py | head -10")
print(output if output else err)

# Test health
print("\n7. Проверка health:")
exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42005/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:42005/health")
print(output if output else err)

# Test chat
print("\n8. Тест chat endpoint:")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, f'''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {api_key.strip()}" \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"Hello"}}],"max_tokens":50}}'
''', timeout=30)
print(output if output else err)

ssh.close()
