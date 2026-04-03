#!/usr/bin/env python3
"""Configure qwen auth type and login."""

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
print("НАСТРОЙКА АУТЕНТИФИКАЦИИ QWEN")
print("=" * 60)

# Check available auth types
print("\n1. Проверка доступных типов аутентификации:")
exit_code, output, err = run_cmd(ssh, "qwen login --help 2>&1 | head -30")
print(output if output else err)

# Check current settings
print("\n2. Текущие настройки:")
exit_code, output, err = run_cmd(ssh, "cat /root/.qwen/settings.json 2>/dev/null || echo 'Not found'")
print(output if output else err)

# Try to set auth type to oauth
print("\n3. Настройка auth type:")
exit_code, output, err = run_cmd(ssh, "qwen settings --auth-type oauth 2>&1 || qwen config --auth-type oauth 2>&1 || echo 'Command not found'")
print(output if output else err)

ssh.close()
