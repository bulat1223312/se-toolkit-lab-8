#!/usr/bin/env python3
"""Check if we can use qwen-code-api without OAuth."""

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
print("ПРОВЕРКА ВОЗМОЖНОСТИ РАБОТЫ БЕЗ OAUTH")
print("=" * 60)

# Check auth.py get_valid_token logic
print("\n1. Проверка auth.py (get_valid_token):")
exit_code, output, err = run_cmd(ssh, "grep -A 20 'async def get_valid_token' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/auth.py")
print(output if output else err)

# Check if there's a way to skip OAuth
print("\n2. Проверка chat.py (OAuth usage):")
exit_code, output, err = run_cmd(ssh, "grep -B 5 -A 10 'get_valid_token\\|access_token' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py | head -30")
print(output if output else err)

# Check qwen-code-api logs for the actual error
print("\n3. Логи qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-qwen-code-api-1 2>&1 | tail -30")
print(output if output else err)

ssh.close()
