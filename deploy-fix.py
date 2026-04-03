#!/usr/bin/env python3
"""Deploy fixed entrypoint.py and restart nanobot on VM."""

import paramiko
import os

VM_HOST = '10.93.25.49'
VM_USER = 'root'
VM_PASSWORD = '23112010A.z'

def run_cmd(ssh, cmd, description=""):
    if description:
        print(f"\n📌 {description}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    print(f"🔹 Команда: {cmd}")
    if output:
        print("📤 STDOUT:", output[:500] if len(output) > 500 else output)
    if err:
        print("📤 STDERR:", err[:500] if len(err) > 500 else err)
    print(f"✅ Exit code: {exit_code}" if exit_code == 0 else f"❌ Exit code: {exit_code}")
    return exit_code, output, err

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VM_HOST, username=VM_USER, password=VM_PASSWORD, timeout=60)

print("=" * 60)
print("ОТПРАВКА ИСПРАВЛЕННОГО entrypoint.py НА VM")
print("=" * 60)

# Read the fixed entrypoint.py
with open(r"c:\Users\user\se-toolkit-lab-8\nanobot\entrypoint.py", "r") as f:
    entrypoint_content = f.read()

# Write to VM using cat with heredoc
print("\n📝 Копирование entrypoint.py на VM...")
sftp = ssh.open_sftp()
sftp.put(r"c:\Users\user\se-toolkit-lab-8\nanobot\entrypoint.py", "/root/se-toolkit-lab-8/nanobot/entrypoint.py")
print("✅ entrypoint.py скопирован на VM")
sftp.close()

# Verify the file
run_cmd(ssh, "grep 'enabled.*True' /root/se-toolkit-lab-8/nanobot/entrypoint.py", "Проверка исправления")

# Restart nanobot service
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot", "Перезапуск nanobot")

# Wait and check logs
run_cmd(ssh, "sleep 8", "Ожидание запуска...")

print("\n" + "=" * 60)
print("ПРОВЕРКА ЛОГОВ ПОСЛЕ ИСПРАВЛЕНИЯ")
print("=" * 60)

run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail 40", "Логи nanobot")

# Check config.resolved.json
print("\n" + "=" * 60)
print("ПРОВЕРКА config.resolved.json")
print("=" * 60)
run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json", "config.resolved.json")

# Check if webchat channel is enabled
print("\n" + "=" * 60)
print("ПРОВЕРКА WEBCHAT КАНАЛА")
print("=" * 60)
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot 2>&1 | grep -i 'webchat\\|channel\\|enabled'", "Webchat в логах")

ssh.close()
print("\n✅ Готово!")
