#!/usr/bin/env python3
"""Rebuild nanobot with fixed entrypoint.py and restart."""

import paramiko

VM_HOST = '10.93.25.49'
VM_USER = 'root'
VM_PASSWORD = '23112010A.z'

def run_cmd(ssh, cmd, description="", timeout=300):
    if description:
        print(f"\n📌 {description}")
    print(f"🔹 Команда: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    if output:
        # Show last 500 chars for long outputs
        display_output = output[-500:] if len(output) > 500 else output
        print("📤 STDOUT:", display_output)
    if err:
        display_err = err[-500:] if len(err) > 500 else err
        print("📤 STDERR:", display_err)
    print(f"{'✅' if exit_code == 0 else '❌'} Exit code: {exit_code}")
    return exit_code, output, err

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VM_HOST, username=VM_USER, password=VM_PASSWORD, timeout=60)

print("=" * 60)
print("ПЕРЕСБОРКА NANOBOT С ИСПРАВЛЕННЫМ entrypoint.py")
print("=" * 60)

# Stop nanobot
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop nanobot", "Остановка nanobot")

# Rebuild nanobot with --no-cache to ensure new entrypoint.py is used
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build --no-cache nanobot", "Пересборка nanobot", timeout=600)

# Start nanobot
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d nanobot", "Запуск nanobot")

# Wait for startup
run_cmd(ssh, "sleep 10", "Ожидание запуска...")

print("\n" + "=" * 60)
print("ПРОВЕРКА ЛОГОВ")
print("=" * 60)
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail 50", "Логи nanobot", timeout=60)

print("\n" + "=" * 60)
print("ПРОВЕРКА config.resolved.json")
print("=" * 60)
run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json", "config.resolved.json")

print("\n" + "=" * 60)
print("ПРОВЕРКА СТАТУСА СЕРВИСОВ")
print("=" * 60)
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps", "Статус сервисов")

ssh.close()
print("\n✅ Готово!")
