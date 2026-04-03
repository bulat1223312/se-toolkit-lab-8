#!/usr/bin/env python3
"""Diagnose LLM API connection issue."""

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
print("ДИАГНОСТИКА LLM API")
print("=" * 60)

# Check qwen-code-api health
print("\n1. Проверка qwen-code-api health:")
exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42005/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:42005/health")
print(output if output else err)

# Check qwen-code-api logs
print("\n2. Логи qwen-code-api (последние 30 строк):")
exit_code, output, err = run_cmd(ssh, "docker compose --env-file /root/se-toolkit-lab-8/.env.docker.secret logs qwen-code-api --tail 30")
print(output if output else err)

# Check config.resolved.json
print("\n3. Проверка config.resolved.json:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json | python3 -m json.tool 2>/dev/null || docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json")
print(output if output else err)

# Check environment variables in nanobot container
print("\n4. Переменные окружения в nanobot контейнере:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 env | grep -E 'LLM|NANOBOT' | sort")
print(output if output else err)

# Test qwen-code-api from inside nanobot container
print("\n5. Тест qwen-code-api из nanobot контейнера:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 python3 -c \"import urllib.request, json; req = urllib.request.Request('http://qwen-code-api:8080/health'); resp = urllib.request.urlopen(req); print(resp.read().decode())\" 2>&1")
print(output if output else err)

# Test qwen-code-api with API key
print("\n6. Тест qwen-code-api с API ключом:")
exit_code, output, err = run_cmd(ssh, '''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: $(grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2)" \\
  -d '{"model":"coder-model","messages":[{"role":"user","content":"Hello"}],"max_tokens":10}' | python3 -m json.tool 2>/dev/null || curl -s -X POST http://localhost:42005/v1/chat/completions -H "Content-Type: application/json" -H "X-API-Key: $(grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2)" -d '{"model":"coder-model","messages":[{"role":"user","content":"Hello"}],"max_tokens":10}'
''')
print(output if output else err)

ssh.close()
