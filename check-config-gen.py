#!/usr/bin/env python3
"""Check entrypoint execution and config generation."""

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
print("ПРОВЕРКА ГЕНЕРАЦИИ CONFIG.RESOLVED.JSON")
print("=" * 60)

# Check full logs for "Using config" message
print("\n1. Логи nanobot (ищем 'Using config'):")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -E 'Using config|config.resolved'")
print(output if output else err)

# Check config.json (source file)
print("\n2. Исходный config.json:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.json")
print(output if output else err)

# Manually run entrypoint to see what happens
print("\n3. Проверка entrypoint.py на VM:")
exit_code, output, err = run_cmd(ssh, "grep -A 10 'Update providers.custom' /root/se-toolkit-lab-8/nanobot/entrypoint.py")
print(output if output else err)

# Check if config.resolved.json is being overwritten
print("\n4. Время создания config.resolved.json:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 ls -la /app/nanobot/config*.json")
print(output if output else err)

ssh.close()
