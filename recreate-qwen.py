#!/usr/bin/env python3
"""Force recreate qwen-code-api container with auth disabled."""

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
print("ПЕРЕСОЗДАНИЕ QWEN-CODE-API С AUTH=FALSE")
print("=" * 60)

# Verify .env.docker.secret has auth disabled
print("\n1. Проверка .env.docker.secret:")
exit_code, output, err = run_cmd(ssh, "grep 'QWEN_CODE_AUTH_USE' /root/se-toolkit-lab-8/.env.docker.secret")
print(output if output else err)

# Down and up qwen-code-api
print("\n2. Пересоздание qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret down qwen-code-api && docker compose --env-file .env.docker.secret up -d qwen-code-api")
print(output if output else err)

# Wait
print("\n3. Ожидание...")
run_cmd(ssh, "sleep 10")

# Check environment in container
print("\n4. Переменные окружения в контейнере:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 env | grep AUTH")
print(output if output else err)

# Test health
print("\n5. Тест health endpoint:")
exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42005/health")
print(output if output else err)

# Test chat without API key
print("\n6. Тест chat endpoint (без ключа):")
exit_code, output, err = run_cmd(ssh, '''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{"model":"coder-model","messages":[{"role":"user","content":"Say hello"}],"max_tokens":50}'
''')
print(output if output else err)

# Restart nanobot
print("\n7. Перезапуск nanobot:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret down nanobot && docker compose --env-file .env.docker.secret up -d nanobot")
print(output if output else err)

# Wait
print("\n8. Ожидание...")
run_cmd(ssh, "sleep 15")

# Check nanobot logs
print("\n9. Логи nanobot:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -E 'error|Error|ERROR|LLM|agent|Agent' | tail -20")
print(output if output else err)

ssh.close()
