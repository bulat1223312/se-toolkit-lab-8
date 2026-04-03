#!/usr/bin/env python3
"""Full check of nanobot on VM."""

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
print("ПОЛНАЯ ПРОВЕРКА NANOBOT")
print("=" * 60)

# Check all logs
print("\n1. ПОЛНЫЕ логи nanobot контейнера:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1")
print(output if output else err)

# Check if entrypoint.py exists and is correct
print("\n2. Проверка entrypoint.py:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 ls -la /app/nanobot/")
print(output)

print("\n3. Содержимое entrypoint.py (первые 50 строк):")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 head -50 /app/nanobot/entrypoint.py")
print(output)

# Check Dockerfile CMD
print("\n4. Dockerfile CMD:")
exit_code, output, err = run_cmd(ssh, "cat /root/se-toolkit-lab-8/nanobot/Dockerfile")
print(output)

# Check pyproject.toml
print("\n5. nanobot/pyproject.toml:")
exit_code, output, err = run_cmd(ssh, "cat /root/se-toolkit-lab-8/nanobot/pyproject.toml")
print(output)

ssh.close()
