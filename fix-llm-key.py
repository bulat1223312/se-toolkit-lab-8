#!/usr/bin/env python3
"""Fix LLM_API_KEY in .env.docker.secret on VM."""

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
print("ИСПРАВЛЕНИЕ LLM_API_KEY В .env.docker.secret")
print("=" * 60)

# Get the correct QWEN_CODE_API_KEY
print("\n1. Получение QWEN_CODE_API_KEY:")
exit_code, output, err = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret")
print(output if output else err)
qwen_key = output.strip().split('=')[1] if '=' in output else None

if qwen_key:
    # Fix LLM_API_KEY to match QWEN_CODE_API_KEY
    print(f"\n2. Исправление LLM_API_KEY на {qwen_key}:")
    exit_code, output, err = run_cmd(ssh, f"""
sed -i 's/^LLM_API_KEY=.*/LLM_API_KEY={qwen_key}/' /root/se-toolkit-lab-8/.env.docker.secret
grep '^LLM_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret
""")
    print(output if output else err)
    
    # Also fix LLM_API_BASE_URL to use service name instead of host.docker.internal
    print("\n3. Исправление LLM_API_BASE_URL:")
    exit_code, output, err = run_cmd(ssh, """
sed -i 's|^LLM_API_BASE_URL=http://host.docker.internal:.*|LLM_API_BASE_URL=http://qwen-code-api:8080/v1|' /root/se-toolkit-lab-8/.env.docker.secret
grep '^LLM_API_BASE_URL=' /root/se-toolkit-lab-8/.env.docker.secret
""")
    print(output if output else err)

# Restart nanobot to pick up new config
print("\n4. Перезапуск nanobot:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot")
print(output if output else err)

# Wait for startup
print("\n5. Ожидание запуска...")
run_cmd(ssh, "sleep 8")

# Check new config.resolved.json
print("\n6. Проверка config.resolved.json:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-nanobot-1 python3 -c \"import json; c=json.load(open('/app/nanobot/config.resolved.json')); print(json.dumps(c.get('providers', {}), indent=2))\"")
print(output if output else err)

# Check logs
print("\n7. Логи nanobot после перезапуска:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -20")
print(output if output else err)

ssh.close()
print("\n✅ Готово!")
