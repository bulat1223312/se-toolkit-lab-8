#!/usr/bin/env python3
"""Check docker-compose.yml for qwen-code-api environment."""

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
print("ПРОВЕРКА QWEN-CODE-API В DOCKER-COMPOSE.YML")
print("=" * 60)

# Check qwen-code-api service definition
print("\n1. qwen-code-api service в docker-compose.yml:")
exit_code, output, err = run_cmd(ssh, "sed -n '/^  qwen-code-api:/,/^  [a-z]/p' /root/se-toolkit-lab-8/docker-compose.yml | head -30")
print(output if output else err)

# Check docker inspect for the container
print("\n2. Docker inspect (Env):")
exit_code, output, err = run_cmd(ssh, "docker inspect se-toolkit-lab-8-qwen-code-api-1 --format='{{range .Config.Env}}{{println .}}{{end}}' | grep -i auth")
print(output if output else err)

ssh.close()
