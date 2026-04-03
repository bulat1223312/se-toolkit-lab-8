#!/usr/bin/env python3
"""Full check of nanobot after rebuild."""

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
print("ПОЛНАЯ ПРОВЕРКА NANOBOT ПОСЛЕ ПЕРЕСБОРКИ")
print("=" * 60)

# Full logs
print("\n1. ПОЛНЫЕ логи nanobot (последнее):")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -80")
print(output if output else err)

# Check config.resolved.json channels section
print("\n2. Channels секция в config.resolved.json:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 python3 -c \"import json; c=json.load(open('/app/nanobot/config.resolved.json')); print(json.dumps(c.get('channels', {}), indent=2))\"")
print(output if output else err)

# Check if webchat channel is listening
print("\n3. Проверка порта 8765 (webchat):")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 netstat -tlnp 2>/dev/null | grep 8765 || ss -tlnp | grep 8765 || echo 'Port check failed'")
print(output if output else err)

# Check running processes
print("\n4. Процессы в контейнере:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 ps aux")
print(output if output else err)

ssh.close()
