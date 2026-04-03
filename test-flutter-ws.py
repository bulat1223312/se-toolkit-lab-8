#!/usr/bin/env python3
"""Test Flutter client and WebSocket connection."""

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
print("ТЕСТИРОВАНИЕ FLUTTER КЛИЕНТА И WEBSOCKET")
print("=" * 60)

# Check Flutter volume
print("\n1. Проверка Flutter volume:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-caddy-1 ls -la /srv/flutter/ | head -20")
print(output if output else err)

# Check if main.dart.js exists
print("\n2. Проверка main.dart.js:")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-caddy-1 ls -la /srv/flutter/*.js 2>&1")
print(output if output else err)

# Test Flutter HTTP
print("\n3. Тест Flutter HTTP:")
exit_code, output, err = run_cmd(ssh, "curl -s -o /dev/null -w 'HTTP Status: %{http_code}\\n' http://localhost:42002/flutter/")
print(output if output else err)

# Test WebSocket with Python
print("\n4. Тест WebSocket:")
exit_code, output, err = run_cmd(ssh, '''
python3 << 'PY'
import asyncio
import json
import websockets

async def test_ws():
    try:
        uri = "ws://localhost:42002/ws/chat?access_key=megakey1"
        async with websockets.connect(uri, close_timeout=10) as ws:
            await ws.send(json.dumps({"content": "What can you do?"}))
            response = await asyncio.wait_for(ws.recv(), timeout=30)
            print("✅ WebSocket response received:")
            print(response[:500] if len(response) > 500 else response)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")

asyncio.run(test_ws())
PY
''')
print(output if output else err)

# Check caddy logs
print("\n5. Логи Caddy:")
exit_code, output, err = run_cmd(ssh, "docker compose --env-file /root/se-toolkit-lab-8/.env.docker.secret logs caddy --tail 20")
print(output if output else err)

ssh.close()
