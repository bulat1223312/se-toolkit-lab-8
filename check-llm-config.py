#!/usr/bin/env python3
"""Check and fix LLM API configuration."""

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
print("ПРОВЕРКА LLM API КОНФИГУРАЦИИ")
print("=" * 60)

# Check .env.docker.secret LLM settings
print("\n1. LLM настройки в .env.docker.secret:")
exit_code, output, err = run_cmd(ssh, "grep -E '^LLM_|^QWEN_CODE_API' /root/se-toolkit-lab-8/.env.docker.secret")
print(output if output else err)

# Check config.resolved.json providers
print("\n2. Providers в config.resolved.json:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 python3 -c \"import json; c=json.load(open('/app/nanobot/config.resolved.json')); print(json.dumps(c.get('providers', {}), indent=2))\"")
print(output if output else err)

# Check qwen-code-api service
print("\n3. Статус qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "docker compose --env-file /root/se-toolkit-lab-8/.env.docker.secret ps qwen-code-api")
print(output if output else err)

# Check qwen-code-api logs
print("\n4. Логи qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "docker compose --env-file /root/se-toolkit-lab-8/.env.docker.secret logs qwen-code-api --tail 20")
print(output if output else err)

# Test qwen-code-api health
print("\n5. Тест qwen-code-api health endpoint:")
exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42005/health | head -20")
print(output if output else err)

# Test qwen-code-api from nanobot container
print("\n6. Тест подключения к qwen-code-api из nanobot контейнера:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 curl -s http://qwen-code-api:8080/health 2>&1 | head -10")
print(output if output else err)

ssh.close()
