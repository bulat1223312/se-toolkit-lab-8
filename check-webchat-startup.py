#!/usr/bin/env python3
"""Check nanobot logs for channel startup."""

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
print("ПРОВЕРКА ЗАПУСКА WEBCHAT КАНАЛА")
print("=" * 60)

# Get full logs and look for channel startup
print("\n1. Логи nanobot (ищем запуск каналов):")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -E 'channel|Channel|enabled|Starting|gateway|webchat|WebSocket' | tail -30")
print(output if output else err)

# Check if nanobot gateway is running
print("\n2. Проверка nanobot gateway:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -E 'Starting nanobot|gateway version|Agent loop' | tail -10")
print(output if output else err)

# Check service status
print("\n3. Статус nanobot сервиса:")
exit_code, output, err = run_cmd(ssh, "docker compose --env-file .env.docker.secret ps nanobot")
print(output if output else err)

# Test WebSocket connection
print("\n4. Тест WebSocket соединения:")
exit_code, output, err = run_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost:42002/flutter || echo 'curl failed'")
print(f"HTTP status: {output}")

ssh.close()
