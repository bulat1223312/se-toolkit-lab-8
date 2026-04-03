#!/usr/bin/env python3
"""Deploy fixed docker-compose.yml and recreate qwen-code-api."""

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
print("ДЕПЛОЙ ИСПРАВЛЕННОГО DOCKER-COMPOSE.YML")
print("=" * 60)

# Pull latest changes
print("\n1. Получение обновлений:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && git pull origin main")
print(output if output else err)

# Verify the fix
print("\n2. Проверка docker-compose.yml:")
exit_code, output, err = run_cmd(ssh, "grep -A 1 'volumes:' /root/se-toolkit-lab-8/docker-compose.yml | grep qwen")
print(output if output else err)

# Recreate qwen-code-api with new volume mount
print("\n3. Пересоздание qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret down qwen-code-api && docker compose --env-file .env.docker.secret up -d qwen-code-api")
print(output if output else err)

# Wait
print("\n4. Ожидание...")
run_cmd(ssh, "sleep 10")

# Check volume mount
print("\n5. Проверка volume mount:")
exit_code, output, err = run_cmd(ssh, "docker inspect se-toolkit-lab-8-qwen-code-api-1 --format='{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}' | grep qwen")
print(output if output else err)

# Check if credentials are accessible
print("\n6. Проверка credentials в контейнере:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 ls -la /root/.qwen/oauth_creds.json 2>/dev/null && docker exec se-toolkit-lab-8-qwen-code-api-1 cat /root/.qwen/oauth_creds.json | python3 -m json.tool 2>/dev/null | head -10 || echo 'Not found'")
print(output if output else err)

# Test health
print("\n7. Проверка health:")
exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42005/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:42005/health")
print(output if output else err)

# Test chat
print("\n8. Тест chat endpoint:")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, f'''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {api_key.strip()}" \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"Hello, how are you?"}}],"max_tokens":100}}'
''', timeout=30)
print(output if output else err)

# Restart nanobot
print("\n9. Перезапуск nanobot:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot")
print(output if output else err)

# Wait
print("\n10. Ожидание...")
run_cmd(ssh, "sleep 10")

# Check nanobot logs
print("\n11. Логи nanobot:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -iE 'error|LLM|agent loop|Processing' | tail -10")
print(output if output else err)

ssh.close()
print("\n" + "=" * 60)
print("ГОТОВО")
print("=" * 60)
