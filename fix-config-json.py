#!/usr/bin/env python3
"""Fix config.json on VM and rebuild nanobot."""

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
print("ИСПРАВЛЕНИЕ config.json НА VM")
print("=" * 60)

# Fix config.json - replace hardcoded values with placeholders
print("\n1. Исправление config.json:")
exit_code, output, err = run_cmd(ssh, '''
cat > /root/se-toolkit-lab-8/nanobot/config.json << 'EOF'
{
  "providers": {
    "custom": {
      "apiKey": "${LLM_API_KEY}",
      "apiBase": "${LLM_API_BASE_URL}"
    }
  },
  "gateway": {
    "host": "0.0.0.0",
    "port": 18790
  },
  "agents": {
    "defaults": {
      "model": "coder-model"
    }
  },
  "channels": {
    "webchat": {
      "host": "0.0.0.0",
      "port": 8765
    }
  },
  "tools": {
    "mcpServers": {
      "lms": {
        "command": "python",
        "args": ["-m", "mcp_lms"],
        "env": {
          "NANOBOT_LMS_BACKEND_URL": "${NANOBOT_LMS_BACKEND_URL}",
          "NANOBOT_LMS_API_KEY": "${NANOBOT_LMS_API_KEY}"
        }
      }
    }
  }
}
EOF
cat /root/se-toolkit-lab-8/nanobot/config.json
''')
print(output if output else err)

# Copy fixed entrypoint.py
print("\n2. Копирование исправленного entrypoint.py:")
sftp = ssh.open_sftp()
sftp.put(r"c:\Users\user\se-toolkit-lab-8\nanobot\entrypoint.py", "/root/se-toolkit-lab-8/nanobot/entrypoint.py")
sftp.close()
print("✅ entrypoint.py скопирован")

# Rebuild nanobot
print("\n3. Пересборка nanobot:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build --no-cache nanobot", timeout=600)
print(output[-1000:] if len(output) > 1000 else output if output else err)

# Restart services
print("\n4. Перезапуск сервисов:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d")
print(output if output else err)

# Wait
print("\n5. Ожидание 20 секунд...")
run_cmd(ssh, "sleep 20")

# Check config.resolved.json
print("\n6. Проверка config.resolved.json:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json 2>&1 | head -20")
print(output if output else err)

# Check logs
print("\n7. Логи nanobot:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -20")
print(output if output else err)

ssh.close()
print("\n✅ Готово!")
