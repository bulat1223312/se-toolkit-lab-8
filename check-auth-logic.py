#!/usr/bin/env python3
"""Check auth logic in qwen-code-api."""

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
print("ПРОВЕРКА ЛОГИКИ AUTH")
print("=" * 60)

# Check routes/chat.py for auth check
print("\n1. Проверка chat.py (auth check):")
exit_code, output, err = run_cmd(ssh, "grep -n 'api_key\\|API_KEY\\|auth' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py | head -20")
print(output if output else err)

# Check middleware
print("\n2. Проверка middleware/auth:")
exit_code, output, err = run_cmd(ssh, "find /root/se-toolkit-lab-8/qwen-code-api/src -name '*.py' -exec grep -l 'api_key\\|API_KEY' {} \\;")
print(output if output else err)

# Read the auth check code
print("\n3. Чтение кода аутентификации:")
exit_code, output, err = run_cmd(ssh, "cat /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py | head -50")
print(output if output else err)

ssh.close()
