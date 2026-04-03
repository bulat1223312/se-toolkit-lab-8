#!/usr/bin/env python3
"""Check validate_api_key in main.py."""

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
print("ПРОВЕРКА validate_api_key")
print("=" * 60)

# Read main.py
print("\n1. Чтение main.py:")
exit_code, output, err = run_cmd(ssh, "cat /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/main.py")
print(output if output else err)

ssh.close()
