#!/usr/bin/env python3
"""Set QWEN_CODE_API_AUTH_USE=false correctly."""

import paramiko

VM_HOST = '10.93.25.49'
VM_USER = 'root'
VM_PASSWORD = '23112010A.z'

def run_cmd(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    return exit_code, output, err

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VM_HOST, username=VM_USER, password=VM_PASSWORD, timeout=60)

print("=" * 60)
print("УСТАНОВКА QWEN_CODE_API_AUTH_USE=false")
print("=" * 60)

# Fix the variable
print("\n1. Исправление QWEN_CODE_API_AUTH_USE:")
exit_code, output, err = run_cmd(ssh, """
cd /root/se-toolkit-lab-8
sed -i 's/^QWEN_CODE_API_AUTH_USE=true/QWEN_CODE_API_AUTH_USE=false/' .env.docker.secret
grep 'QWEN_CODE.*AUTH' .env.docker.secret
""")
print(output if output else err)

# Recreate qwen-code-api
print("\n2. Пересоздание qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret down qwen-code-api && docker compose --env-file .env.docker.secret up -d qwen-code-api")
print(output if output else err)

# Wait
print("\n3. Ожидание...")
run_cmd(ssh, "sleep 10")

# Check environment
print("\n4. Проверка переменных в контейнере:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 env | grep AUTH")
print(output if output else err)

# Test chat endpoint
print("\n5. Тест chat endpoint:")
exit_code, output, err = run_cmd(ssh, '''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{"model":"coder-model","messages":[{"role":"user","content":"Hello, how are you?"}],"max_tokens":100}'
''')
print(output if output else err)

ssh.close()
