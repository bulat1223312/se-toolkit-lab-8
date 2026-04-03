#!/usr/bin/env python3
"""Final test of the full stack."""

import paramiko
import time

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
print("ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ")
print("=" * 60)

# Wait for full startup
print("\n1. Ожидание 15 секунд...")
time.sleep(15)

# Check full logs
print("\n2. Логи nanobot (последние 40 строк):")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -40")
print(output)

# Test WebSocket
print("\n3. Тест WebSocket:")
exit_code, output, err = run_cmd(ssh, '''
timeout 30 websocat -t 5 "ws://localhost:42002/ws/chat?access_key=megakey1" << 'MSG'
{"content": "What can you do in this system?"}
MSG
''', timeout=60)
print(output if output else err)

# Check Flutter
print("\n4. Проверка Flutter:")
exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42002/flutter/ | head -20")
print(output if output else err)

# Check service status
print("\n5. Статус сервисов:")
exit_code, output, err = run_cmd(ssh, "docker compose --env-file /root/se-toolkit-lab-8/.env.docker.secret ps")
print(output if output else err)

ssh.close()
