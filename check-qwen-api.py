#!/usr/bin/env python3
"""Check qwen-code-api configuration and logs."""

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
print("ПРОВЕРКА QWEN-CODE-API")
print("=" * 60)

# Check qwen-code-api environment
print("\n1. Переменные окружения qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 env | grep -E 'QWEN|DEFAULT|API' | sort")
print(output if output else err)

# Check qwen-code-api config file
print("\n2. Проверка конфигурации qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 ls -la /app/ 2>/dev/null || docker exec se-toolkit-lab-8-qwen-code-api-1 ls -la /")
print(output if output else err)

# Check full qwen-code-api logs
print("\n3. Полные логи qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-qwen-code-api-1 2>&1 | tail -50")
print(output if output else err)

# Check if there's a config file
print("\n4. Поиск конфигурационных файлов:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 find / -name '*.json' -o -name '*.yaml' -o -name '*.yml' 2>/dev/null | grep -v node_modules | grep -v proc | head -20")
print(output if output else err)

# Check .env.docker.secret for Qwen settings
print("\n5. Qwen настройки в .env.docker.secret:")
exit_code, output, err = run_cmd(ssh, "grep -E '^QWEN' /root/se-toolkit-lab-8/.env.docker.secret")
print(output if output else err)

# Check qwen-code-api source
print("\n6. Структура qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "ls -la /root/se-toolkit-lab-8/qwen-code-api/")
print(output if output else err)

ssh.close()
