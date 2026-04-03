#!/usr/bin/env python3
"""Refresh OAuth token using curl."""

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
print("ОБНОВЛЕНИЕ OAUTH TOKEN ЧЕРЕЗ CURL")
print("=" * 60)

# Get refresh token
print("\n1. Получение refresh token:")
exit_code, output, err = run_cmd(ssh, "python3 -c \"import json; print(json.load(open('/root/.qwen/oauth_creds.json'))['refresh_token'])\"")
refresh_token = output.strip() if output else ""
print(f"Refresh token: {refresh_token[:30]}...")

# Try to refresh
print("\n2. Попытка обновления токена:")
exit_code, output, err = run_cmd(ssh, f'''
curl -s -X POST https://chat.qwen.ai/api/v1/oauth2/token \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -H "Accept: application/json" \\
  -d "grant_type=refresh_token&refresh_token={refresh_token}&client_id=f0304373b74a44d2b584a3fb70ca9e56"
''')
print(output if output else err)

ssh.close()
