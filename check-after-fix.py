#!/usr/bin/env python3
"""Check qwen-code-api logs after fix."""

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
print("ПРОВЕРКА ЛОГОВ ПОСЛЕ ИСПРАВЛЕНИЯ")
print("=" * 60)

# Check full logs
print("\n1. Логи qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-qwen-code-api-1 2>&1 | tail -50")
print(output if output else err)

# Check if the file was updated correctly
print("\n2. Проверка chat.py:")
exit_code, output, err = run_cmd(ssh, "grep -A 5 'qwen_code_auth_use' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py | head -20")
print(output if output else err)

# Test with verbose output
print("\n3. Тест с подробным выводом:")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, f'''
curl -v -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {api_key.strip()}" \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"Hello"}}],"max_tokens":50}}' 2>&1 | tail -30
''', timeout=30)
print(output if output else err)

ssh.close()
