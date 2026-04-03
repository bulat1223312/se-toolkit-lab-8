#!/usr/bin/env python3
"""Check qwen-code-api auth configuration."""

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
print("ПРОВЕРКА КОНФИГУРАЦИИ AUTH")
print("=" * 60)

# Check qwen-code-api config module
print("\n1. Проверка config.py:")
exit_code, output, err = run_cmd(ssh, "cat /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/config.py")
print(output if output else err)

# Check environment variables in container
print("\n2. Переменные окружения в контейнере:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 env | grep -E 'QWEN|AUTH|API_KEY' | sort")
print(output if output else err)

# Check docker-compose.yml for qwen-code-api
print("\n3. qwen-code-api в docker-compose.yml:")
exit_code, output, err = run_cmd(ssh, "grep -A 30 'qwen-code-api:' /root/se-toolkit-lab-8/docker-compose.yml | head -35")
print(output if output else err)

ssh.close()
