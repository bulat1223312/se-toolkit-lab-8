#!/usr/bin/env python3
"""Fix OAuth credentials mount issue."""

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
print("ИСПРАВЛЕНИЕ OAUTH CREDENTIALS")
print("=" * 60)

# Check volume mount
print("\n1. Проверка volume mount:")
exit_code, output, err = run_cmd(ssh, "docker inspect se-toolkit-lab-8-qwen-code-api-1 --format='{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}' | grep qwen")
print(output if output else err)

# Check host oauth_creds.json
print("\n2. oauth_creds.json на хосте:")
exit_code, output, err = run_cmd(ssh, "ls -la /root/.qwen/oauth_creds.json 2>/dev/null && cat /root/.qwen/oauth_creds.json | python3 -m json.tool 2>/dev/null | head -15 || echo 'Not found'")
print(output if output else err)

# Check container oauth_creds.json
print("\n3. oauth_creds.json в контейнере:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 ls -la /mnt/qwen-creds/ 2>/dev/null || docker exec se-toolkit-lab-8-qwen-code-api-1 ls -la /home/nonroot/.qwen/ 2>/dev/null || echo 'Not found'")
print(output if output else err)

# Copy oauth_creds.json to container
print("\n4. Копирование oauth_creds.json в контейнер:")
exit_code, output, err = run_cmd(ssh, """
docker cp /root/.qwen/oauth_creds.json se-toolkit-lab-8-qwen-code-api-1:/home/nonroot/.qwen/oauth_creds.json
docker exec se-toolkit-lab-8-qwen-code-api-1 cat /home/nonroot/.qwen/oauth_creds.json | python3 -m json.tool 2>/dev/null | head -10
""")
print(output if output else err)

# Restart qwen-code-api
print("\n5. Перезапуск qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "docker restart se-toolkit-lab-8-qwen-code-api-1")
print(output if output else err)

# Wait
print("\n6. Ожидание...")
run_cmd(ssh, "sleep 5")

# Test chat
print("\n7. Тест chat endpoint:")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, f'''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {api_key.strip()}" \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"Hello"}}],"max_tokens":50}}'
''')
print(output if output else err)

ssh.close()
