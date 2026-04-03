#!/usr/bin/env python3
"""Apply minimal fix to chat.py in container."""

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
print("МИНИМАЛЬНОЕ ИСПРАВЛЕНИЕ CHAT.PY")
print("=" * 60)

# Restore backup and apply minimal fix
print("\n1. Восстановление оригинала и применение исправлений:")
exit_code, output, err = run_cmd(ssh, '''
# Restore original
docker exec se-toolkit-lab-8-qwen-code-api-1 cp /app/qwen_code_api/routes/chat.py.bak /app/qwen_code_api/routes/chat.py

# Apply minimal fix using sed
# Replace the auth token line
docker exec se-toolkit-lab-8-qwen-code-api-1 sed -i 's/access_token = await auth.get_valid_token(client)/if settings.qwen_code_auth_use:\\n        access_token = await auth.get_valid_token(client)\\n    else:\\n        access_token = settings.qwen_code_api_key/' /app/qwen_code_api/routes/chat.py

# Replace the URL line
docker exec se-toolkit-lab-8-qwen-code-api-1 sed -i 's/creds = auth.load_credentials()/if settings.qwen_code_auth_use:\\n        creds = auth.load_credentials()\\n        url = f"{auth.get_api_endpoint(creds)}\\/chat\\/completions"\\n    else:\\n        url = f"{settings.qwen_api_base}\\/chat\\/completions"/' /app/qwen_code_api/routes/chat.py

# Replace the headers line
docker exec se-toolkit-lab-8-qwen-code-api-1 sed -i 's/headers = build_headers(access_token, streaming=is_streaming)/if settings.qwen_code_auth_use:\\n        headers = build_headers(access_token, streaming=is_streaming)\\n    else:\\n        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application\\/json"}\\n        if is_streaming:\\n            headers["Accept"] = "text\\/event-stream"/' /app/qwen_code_api/routes/chat.py

# Verify
echo "=== Checking fixes ==="
docker exec se-toolkit-lab-8-qwen-code-api-1 grep -n 'qwen_code_auth_use' /app/qwen_code_api/routes/chat.py
''')
print(output if output else err)

# Restart
print("\n2. Перезапуск:")
exit_code, output, err = run_cmd(ssh, "docker restart se-toolkit-lab-8-qwen-code-api-1")
print(output if output else err)

# Wait
print("\n3. Ожидание...")
run_cmd(ssh, "sleep 8")

# Test
print("\n4. Тест:")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, f'''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {api_key.strip()}" \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"Hello"}}],"max_tokens":50}}'
''', timeout=30)
print(output if output else err)

# Logs
print("\n5. Логи:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-qwen-code-api-1 2>&1 | tail -15")
print(output if output else err)

ssh.close()
