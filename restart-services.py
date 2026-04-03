#!/usr/bin/env python3
"""Restart services with correct env file path."""

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
print("ПЕРЕЗАПУСК СЕРВИСОВ С ПРАВИЛЬНЫМ ПУТЕМ")
print("=" * 60)

# Restart qwen-code-api with correct path
print("\n1. Перезапуск qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart qwen-code-api")
print(output if output else err)

# Wait
print("\n2. Ожидание...")
run_cmd(ssh, "sleep 10")

# Test chat endpoint
print("\n3. Тест chat endpoint:")
exit_code, output, err = run_cmd(ssh, '''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{"model":"coder-model","messages":[{"role":"user","content":"Say hello"}],"max_tokens":50}'
''')
print(output if output else err)

# Restart nanobot
print("\n4. Перезапуск nanobot:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot")
print(output if output else err)

# Wait
print("\n5. Ожидание...")
run_cmd(ssh, "sleep 10")

# Check nanobot logs
print("\n6. Логи nanobot (последние 15 строк):")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -15")
print(output if output else err)

ssh.close()
