#!/usr/bin/env python3
"""Try to refresh OAuth token or suggest alternative."""

import paramiko
import time

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
print("ПРОВЕРКА OAUTH TOKEN REFRESH")
print("=" * 60)

# Check expiry date
print("\n1. Проверка срока действия токена:")
exit_code, output, err = run_cmd(ssh, """
python3 << 'PY'
import json
from datetime import datetime

with open('/root/.qwen/oauth_creds.json') as f:
    creds = json.load(f)

expiry_ms = creds['expiry_date']
expiry_s = expiry_ms / 1000
expiry_date = datetime.fromtimestamp(expiry_s)
now = datetime.now()

print(f"Token expiry: {expiry_date}")
print(f"Current time: {now}")
print(f"Token valid: {now < expiry_date}")
print(f"Refresh token exists: {bool(creds.get('refresh_token'))}")
PY
""")
print(output if output else err)

# Try to refresh token manually
print("\n2. Попытка обновить токен через OAuth refresh:")
exit_code, output, err = run_cmd(ssh, """
python3 << 'PY'
import httpx
import json

with open('/root/.qwen/oauth_creds.json') as f:
    creds = json.load(f)

refresh_token = creds.get('refresh_token', '')
client_id = 'f0304373b74a44d2b584a3fb70ca9e56'

print(f"Refresh token: {refresh_token[:20]}...")
print(f"Client ID: {client_id}")

# Try to refresh
try:
    with httpx.Client() as client:
        resp = client.post(
            'https://chat.qwen.ai/api/v1/oauth2/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': client_id,
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
            },
            timeout=10
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
        
        if resp.status_code == 200:
            new_creds = resp.json()
            print("New token received!")
            # Save new credentials
            creds.update(new_creds)
            with open('/root/.qwen/oauth_creds.json', 'w') as f:
                json.dump(creds, f, indent=2)
            print("New credentials saved!")
except Exception as e:
    print(f"Error: {e}")
PY
""")
print(output if output else err)

ssh.close()
