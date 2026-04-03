#!/usr/bin/env python3
"""Check nanobot status and logs on VM."""

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
print("ПРОВЕРКА NANOBOT")
print("=" * 60)

# Check container logs
print("\n1. Логи nanobot контейнера:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -100")
print(output if output else err)

# Check if container is running
print("\n2. Статус контейнера:")
exit_code, output, err = run_cmd(ssh, "docker inspect se-toolkit-lab-8-nanobot-1 --format='{{.State.Status}}: {{.State.ExitCode}}'")
print(output)

# Check config.resolved.json
print("\n3. Проверка config.resolved.json:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json 2>&1")
print(output if output else err)

# Check environment variables
print("\n4. Переменные окружения в контейнере:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 env | grep -E 'LLM|NANOBOT' | sort")
print(output)

# Check if nanobot process is running
print("\n5. Процесс nanobot в контейнере:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 ps aux | grep nanobot")
print(output)

# Check .env.docker.secret values
print("\n6. Значения в .env.docker.secret:")
exit_code, output, err = run_cmd(ssh, "grep -E '^LLM_API|^NANOBOT_ACCESS|^QWEN_CODE_API' /root/se-toolkit-lab-8/.env.docker.secret")
print(output)

ssh.close()
