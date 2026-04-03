#!/usr/bin/env python3
"""Fix credentials path issue in qwen-code-api container."""

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
print("ИСПРАВЛЕНИЕ ПУТИ К CREDENTIALS")
print("=" * 60)

# Check where the container looks for credentials
print("\n1. Проверка путей в контейнере:")
exit_code, output, err = run_cmd(ssh, """
echo "=== Volume mounts ==="
docker inspect se-toolkit-lab-8-qwen-code-api-1 --format='{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}' | grep qwen

echo "=== Home directory in container ==="
docker exec se-toolkit-lab-8-qwen-code-api-1 sh -c 'echo HOME=$HOME && ls -la $HOME/.qwen/ 2>/dev/null || echo "No .qwen in home"'

echo "=== Check /mnt/qwen-creds ==="
docker exec se-toolkit-lab-8-qwen-code-api-1 ls -la /mnt/qwen-creds/ 2>/dev/null || echo "No /mnt/qwen-creds"

echo "=== Check config.py creds_file path ==="
docker exec se-toolkit-lab-8-qwen-code-api-1 python3 -c "from qwen_code_api.config import settings; print(f'creds_file: {settings.creds_file}')" 2>/dev/null || echo "Cannot check config"
""")
print(output if output else err)

# Copy credentials to the correct location
print("\n2. Копирование credentials в правильное место:")
exit_code, output, err = run_cmd(ssh, """
# Copy to container's home directory
docker cp /root/.qwen/oauth_creds.json se-toolkit-lab-8-qwen-code-api-1:/home/nonroot/.qwen/oauth_creds.json
docker exec se-toolkit-lab-8-qwen-code-api-1 cat /home/nonroot/.qwen/oauth_creds.json | python3 -m json.tool 2>/dev/null | head -10
""")
print(output if output else err)

# Restart container
print("\n3. Перезапуск qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "docker restart se-toolkit-lab-8-qwen-code-api-1")
print(output if output else err)

# Wait
print("\n4. Ожидание...")
run_cmd(ssh, "sleep 8")

# Test health
print("\n5. Проверка health:")
exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42005/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:42005/health")
print(output if output else err)

# Test chat
print("\n6. Тест chat endpoint:")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, f'''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {api_key.strip()}" \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"Hello"}}],"max_tokens":50}}'
''', timeout=30)
print(output if output else err)

ssh.close()
