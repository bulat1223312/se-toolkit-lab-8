#!/usr/bin/env python3
"""Check qwen-code-api logs for credential loading."""

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
print("ПРОВЕРКА ЛОГОВ QWEN-CODE-API")
print("=" * 60)

# Check full logs
print("\n1. Полные логи qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-qwen-code-api-1 2>&1 | grep -iE 'credential|token|auth|error|Error' | head -30")
print(output if output else err)

# Check if the container can read the file
print("\n2. Проверка чтения файла в контейнере:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 python3 -c \"from qwen_code_api.config import settings; print(f'creds_file: {settings.creds_file}'); print(f'exists: {settings.creds_file.exists()}'); print(f'auth_use: {settings.qwen_code_auth_use}')\"")
print(output if output else err)

# Check auth.py logic
print("\n3. Проверка auth.py (is_token_valid):")
exit_code, output, err = run_cmd(ssh, "grep -A 10 'def is_token_valid' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/auth.py")
print(output if output else err)

# Check if token is considered valid
print("\n4. Проверка валидности токена:")
exit_code, output, err = run_cmd(ssh, """
docker exec se-toolkit-lab-8-qwen-code-api-1 python3 << 'PYEOF'
import json
import time
from pathlib import Path

creds_file = Path('/root/.qwen/oauth_creds.json')
print(f"File exists: {creds_file.exists()}")

if creds_file.exists():
    with open(creds_file) as f:
        creds = json.load(f)
    
    expiry_ms = creds.get('expiry_date', 0)
    expiry_s = expiry_ms / 1000
    now = time.time()
    
    print(f"Expiry: {expiry_s}")
    print(f"Now: {now}")
    print(f"Valid: {now < expiry_s}")
    print(f"Has access_token: {bool(creds.get('access_token'))}")
    print(f"Has refresh_token: {bool(creds.get('refresh_token'))}")
PYEOF
""")
print(output if output else err)

ssh.close()
