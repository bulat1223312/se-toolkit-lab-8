#!/usr/bin/env python3
"""Fix nanobot on VM - enable webchat channel."""

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
print="ИСПРАВЛЕНИЕ NANOBOT - ВКЛЮЧЕНИЕ WEBCHAT КАНАЛА")
print("=" * 60)

# Проверка текущего config.resolved.json
print("\n1. Текущий config.resolved.json (channels секция):")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json | grep -A 5 'channels'")
print(output if output else err)

# Исправление entrypoint.py - добавление enabled: True для webchat
print("\n2. Проверка entrypoint.py на VM:")
exit_code, output, err = run_cmd(ssh, "grep -A 5 'webchat.*host' /root/se-toolkit-lab-8/nanobot/entrypoint.py")
print(output if output else err)

# Перезапуск nanobot с правильными настройками
print("\n3. Перезапуск nanobot сервиса:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot")
print(output if output else err)

# Проверка логов после перезапуска
print("\n4. Логи после перезапуска:")
exit_code, output, err = run_cmd(ssh, "sleep 5 && docker compose --env-file .env.docker.secret logs nanobot --tail 30")
print(output if output else err)

ssh.close()
