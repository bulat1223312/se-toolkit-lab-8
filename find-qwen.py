#!/usr/bin/env python3
"""Find qwen binary and configure auth."""

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
print("ПОИСК QWEN CLI")
print("=" * 60)

# Find qwen binary
print("\n1. Поиск qwen:")
exit_code, output, err = run_cmd(ssh, "which qwen 2>/dev/null || find / -name 'qwen' -type f 2>/dev/null | head -5 || echo 'Not found'")
print(output if output else err)

# Check npm global
print("\n2. Проверка npm global:")
exit_code, output, err = run_cmd(ssh, "npm list -g --depth=0 2>/dev/null | grep qwen || echo 'Not in npm'")
print(output if output else err)

# Check npx
print("\n3. Проверка npx:")
exit_code, output, err = run_cmd(ssh, "npx @anthropic-ai/qwen-code --help 2>&1 | head -10 || npx qwen-code --help 2>&1 | head -10 || echo 'Not found via npx'")
print(output if output else err)

# Check common locations
print("\n4. Проверка распространенных мест:")
exit_code, output, err = run_cmd(ssh, "ls -la /usr/local/bin/qwen* /usr/bin/qwen* /root/.npm*/bin/qwen* /root/.nvm/*/bin/qwen* 2>/dev/null || echo 'Not in common locations'")
print(output if output else err)

# Check if it's a node package
print("\n5. Проверка node packages:")
exit_code, output, err = run_cmd(ssh, "find /root -name 'qwen-code' -type d 2>/dev/null | head -5 || echo 'Not found'")
print(output if output else err)

# Check PATH
print("\n6. PATH:")
exit_code, output, err = run_cmd(ssh, "echo $PATH")
print(output if output else err)

ssh.close()
