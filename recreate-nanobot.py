#!/usr/bin/env python3
"""Force recreate nanobot container with new env vars."""

import paramiko

VM_HOST = '10.93.25.49'
VM_USER = 'root'
VM_PASSWORD = '23112010A.z'

def run_cmd(ssh, cmd, timeout=120):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    return exit_code, output, err

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VM_HOST, username=VM_USER, password=VM_PASSWORD, timeout=60)

print("=" * 60)
print("ПЕРЕСОЗДАНИЕ NANOBOT КОНТЕЙНЕРА")
print("=" * 60)

# Stop and remove container
print("\n1. Остановка и удаление контейнера:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret down nanobot")
print(output if output else err)

# Remove old image
print("\n2. Удаление старого образа:")
exit_code, output, err = run_cmd(ssh, "docker rmi se-toolkit-lab-8-nanobot:latest 2>/dev/null || echo 'Image removed or not found'")
print(output if output else err)

# Rebuild with --no-cache
print("\n3. Пересборка образа (это займет время):")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build --no-cache nanobot", timeout=600)
print(output[-1000:] if len(output) > 1000 else output if output else err)

# Start services
print("\n4. Запуск сервисов:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d")
print(output if output else err)

# Wait for startup
print("\n5. Ожидание 20 секунд...")
run_cmd(ssh, "sleep 20")

# Check config.resolved.json
print("\n6. Проверка config.resolved.json:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json 2>&1 | head -30")
print(output if output else err)

# Check logs
print("\n7. Логи nanobot:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -30")
print(output if output else err)

ssh.close()
print("\n✅ Готово!")
