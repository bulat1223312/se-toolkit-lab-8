#!/usr/bin/env python3
"""Quick check for qwen CLI."""

import paramiko

VM_HOST = '10.93.25.49'
VM_USER = 'root'
VM_PASSWORD = '23112010A.z'

def run_cmd(ssh, cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    return exit_code, output, err

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VM_HOST, username=VM_USER, password=VM_PASSWORD, timeout=60)

print("1. Проверка qwen через bash -l:")
exit_code, output, err = run_cmd(ssh, "bash -l -c 'which qwen' 2>&1")
print(output if output else err)

print("\n2. Проверка npx qwen:")
exit_code, output, err = run_cmd(ssh, "bash -l -c 'npx @anthropic-ai/qwen-code --version' 2>&1 | head -5")
print(output if output else err)

print("\n3. Проверка ~/.npm-global/bin:")
exit_code, output, err = run_cmd(ssh, "ls ~/.npm-global/bin/qwen* 2>/dev/null || ls /usr/local/bin/qwen* 2>/dev/null || echo 'Not found'")
print(output if output else err)

print("\n4. Попытка запуска qwen login через npx:")
exit_code, output, err = run_cmd(ssh, "bash -l -c 'npx @anthropic-ai/qwen-code login --help' 2>&1 | head -20", timeout=30)
print(output if output else err)

ssh.close()
