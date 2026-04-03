#!/usr/bin/env python3
"""Directly edit docker-compose.yml on VM to mount qwen-code-api source."""

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
print("ПРЯМОЕ РЕДАКТИРОВАНИЕ DOCKER-COMPOSE.YML")
print("=" * 60)

# Use Python to edit the file
print("\n1. Редактирование docker-compose.yml:")
exit_code, output, err = run_cmd(ssh, '''
cd /root/se-toolkit-lab-8

python3 << 'PYEOF'
with open('docker-compose.yml', 'r') as f:
    lines = f.readlines()

new_lines = []
in_qwen_section = False
in_volumes = False
added_mount = False

for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Detect qwen-code-api section
    if line.strip() == 'qwen-code-api:':
        in_qwen_section = True
    
    # Detect volumes section under qwen-code-api
    if in_qwen_section and line.strip() == 'volumes:':
        in_volumes = True
    
    # Add mount after the qwen volume
    if in_volumes and '~/.qwen:/root/.qwen:ro' in line and not added_mount:
        new_lines.append('      - ./qwen-code-api/src:/app/qwen_code_api:ro\n')
        added_mount = True
        in_volumes = False
        in_qwen_section = False

with open('docker-compose.yml', 'w') as f:
    f.writelines(new_lines)

print("✅ File updated")
PYEOF

# Verify
echo "=== Volumes section ==="
grep -A 3 'volumes:' /root/se-toolkit-lab-8/docker-compose.yml | head -10
''')
print(output if output else err)

# Recreate container
print("\n2. Пересоздание контейнера:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret down qwen-code-api && docker compose --env-file .env.docker.secret up -d qwen-code-api")
print(output if output else err)

# Wait
print("\n3. Ожидание...")
run_cmd(ssh, "sleep 10")

# Check mount
print("\n4. Проверка монтирования:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 cat /app/qwen_code_api/routes/chat.py | grep -A 5 'qwen_code_auth_use' | head -15")
print(output if output else err)

# Test
print("\n5. Тест chat endpoint:")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, f'''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {api_key.strip()}" \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"Hello"}}],"max_tokens":50}}'
''', timeout=30)
print(output if output else err)

ssh.close()
