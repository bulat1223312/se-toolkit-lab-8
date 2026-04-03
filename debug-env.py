#!/usr/bin/env python3
"""Debug environment variables in nanobot container."""

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
print("ОТЛАДКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
print("=" * 60)

# Check what env vars are passed to container
print("\n1. Переменные окружения в контейнере nanobot:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 env | grep -E 'LLM|NANOBOT' | sort")
print(output if output else err)

# Check docker-compose.yml nanobot service environment
print("\n2. Environment в docker-compose.yml (nanobot service):")
exit_code, output, err = run_cmd(ssh, "grep -A 20 '^  nanobot:' /root/se-toolkit-lab-8/docker-compose.yml | grep -E '^\\s+-\\s+[A-Z_]+'")
print(output if output else err)

# Check .env.docker.secret values
print("\n3. Значения в .env.docker.secret:")
exit_code, output, err = run_cmd(ssh, "grep -E '^LLM_|^NANOBOT_' /root/se-toolkit-lab-8/.env.docker.secret")
print(output if output else err)

# Inspect container
print("\n4. Inspect контейнера (environment):")
exit_code, output, err = run_cmd(ssh, "docker inspect se-toolkit-lab-8-nanobot-1 --format='{{range .Config.Env}}{{println .}}{{end}}' | grep -E 'LLM|NANOBOT'")
print(output if output else err)

ssh.close()
