#!/usr/bin/env python3
"""Fix variable name mismatch in .env.docker.secret."""

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
print("ИСПРАВЛЕНИЕ ИМЕНИ ПЕРЕМЕННОЙ")
print("=" * 60)

# Add the correct variable name
print("\n1. Добавление QWEN_CODE_API_AUTH_USE=false:")
exit_code, output, err = run_cmd(ssh, """
cd /root/se-toolkit-lab-8
# Add the correct variable name that docker-compose.yml expects
grep -q 'QWEN_CODE_API_AUTH_USE' .env.docker.secret || echo 'QWEN_CODE_API_AUTH_USE=false' >> .env.docker.secret
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
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 env | grep -E 'AUTH|API_KEY' | sort")
print(output if output else err)

# Test chat endpoint
print("\n5. Тест chat endpoint:")
exit_code, output, err = run_cmd(ssh, '''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{"model":"coder-model","messages":[{"role":"user","content":"Say hello"}],"max_tokens":50}'
''')
print(output if output else err)

# Restart nanobot
print("\n6. Перезапуск nanobot:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot")
print(output if output else err)

# Wait
print("\n7. Ожидание...")
run_cmd(ssh, "sleep 15")

# Check nanobot logs for errors
print("\n8. Логи nanobot (ошибки):")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -iE 'error|LLM|agent loop' | tail -10")
print(output if output else err)

ssh.close()
