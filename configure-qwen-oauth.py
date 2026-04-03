#!/usr/bin/env python3
"""Configure qwen auth type and login."""

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
print("НАСТРОЙКА QWEN AUTH И ВХОД")
print("=" * 60)

# Step 1: Update settings.json with auth type
print("\n1. Настройка settings.json:")
exit_code, output, err = run_cmd(ssh, '''
cat > /root/.qwen/settings.json << 'EOF'
{
  "security": {
    "auth": {
      "type": "qwen-oauth"
    }
  },
  "model": {
    "name": "coder-model"
  },
  "$version": 3
}
EOF
cat /root/.qwen/settings.json
''')
print(output if output else err)

# Step 2: Try qwen login with auth-type flag
print("\n2. Попытка qwen login --auth-type qwen-oauth:")
exit_code, output, err = run_cmd(ssh, "qwen login --auth-type qwen-oauth 2>&1 | head -20", timeout=30)
print(output if output else err)

ssh.close()
