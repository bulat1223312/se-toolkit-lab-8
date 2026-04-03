#!/usr/bin/env python3
"""Check and fix OAuth credentials for qwen-code-api."""

import paramiko
import json

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
print("ПРОВЕРКА OAUTH CREDENTIALS")
print("=" * 60)

# Check oauth_creds.json
print("\n1. Проверка oauth_creds.json:")
exit_code, output, err = run_cmd(ssh, "cat /root/.qwen/oauth_creds.json 2>/dev/null || echo 'File not found'")
print(output if output else err)

# Check container oauth_creds.json
print("\n2. oauth_creds.json в контейнере:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 cat /mnt/qwen-creds/oauth_creds.json 2>/dev/null || docker exec se-toolkit-lab-8-qwen-code-api-1 cat /home/nonroot/.qwen/oauth_creds.json 2>/dev/null || echo 'Not found'")
print(output if output else err)

# Check settings.json
print("\n3. settings.json:")
exit_code, output, err = run_cmd(ssh, "cat /root/.qwen/settings.json 2>/dev/null | python3 -m json.tool 2>/dev/null || cat /root/.qwen/settings.json 2>/dev/null || echo 'Not found'")
print(output if output else err)

# Check if we need to re-authenticate
print("\n4. Проверка auth.py:")
exit_code, output, err = run_cmd(ssh, "cat /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/auth.py | head -80")
print(output if output else err)

ssh.close()
