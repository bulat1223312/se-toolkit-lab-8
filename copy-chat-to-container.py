#!/usr/bin/env python3
"""Copy fixed chat.py directly into running container."""

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
print("КОПИРОВАНИЕ ИСПРАВЛЕННОГО CHAT.PY В КОНТЕЙНЕР")
print("=" * 60)

# Copy the fixed file into container
print("\n1. Копирование chat.py в контейнер:")
exit_code, output, err = run_cmd(ssh, '''
# First backup original
docker exec se-toolkit-lab-8-qwen-code-api-1 cp /app/qwen_code_api/routes/chat.py /app/qwen_code_api/routes/chat.py.bak

# Copy fixed version
cp /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py /tmp/fixed_chat.py
docker cp /tmp/fixed_chat.py se-toolkit-lab-8-qwen-code-api-1:/app/qwen_code_api/routes/chat.py

# Verify
docker exec se-toolkit-lab-8-qwen-code-api-1 grep -A 3 'qwen_code_auth_use' /app/qwen_code_api/routes/chat.py | head -10
''')
print(output if output else err)

# Restart container to pick up changes
print("\n2. Перезапуск контейнера:")
exit_code, output, err = run_cmd(ssh, "docker restart se-toolkit-lab-8-qwen-code-api-1")
print(output if output else err)

# Wait
print("\n3. Ожидание...")
run_cmd(ssh, "sleep 8")

# Test
print("\n4. Тест chat endpoint:")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, f'''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {api_key.strip()}" \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"Hello"}}],"max_tokens":50}}'
''', timeout=30)
print(output if output else err)

# Check logs
print("\n5. Логи qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-qwen-code-api-1 2>&1 | tail -20")
print(output if output else err)

ssh.close()
