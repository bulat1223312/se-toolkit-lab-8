#!/usr/bin/env python3
"""Test WebSocket connection using websocat or curl."""

import paramiko
import subprocess

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
print("ТЕСТИРОВАНИЕ WEBSOCKET ЧЕРЕЗ WEBSOCAT")
print("=" * 60)

# Check if websocat is available
print("\n1. Проверка websocat:")
exit_code, output, err = run_cmd(ssh, "which websocat || echo 'websocat not found'")
print(output if output else err)

# Install websocat if not available
if "not found" in output:
    print("\n2. Установка websocat...")
    exit_code, output, err = run_cmd(ssh, """
cd /tmp
curl -L https://github.com/vi/websocat/releases/download/v1.13.0/websocat.x86_64-unknown-linux-musl -o websocat
chmod +x websocat
mv websocat /usr/local/bin/
websocat --version
""")
    print(output if output else err)

# Test WebSocket with websocat
print("\n3. Тест WebSocket через websocat:")
exit_code, output, err = run_cmd(ssh, '''
echo '{"content":"What can you do in this system?"}' | timeout 30 websocat "ws://localhost:42002/ws/chat?access_key=megakey1" || echo "websocat test completed"
''', timeout=60)
print(output if output else err)

# Check nanobot logs for message processing
print("\n4. Логи nanobot (последние 30 строк):")
exit_code, output, err = run_cmd(ssh, "docker compose --env-file /root/se-toolkit-lab-8/.env.docker.secret logs nanobot --tail 30")
print(output if output else err)

ssh.close()
