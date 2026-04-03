#!/usr/bin/env python3
"""Test WebSocket connection properly."""

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
print("ТЕСТ WEBSOCKET СОЕДИНЕНИЯ")
print("=" * 60)

# Test WebSocket using Python on VM
print("\n1. Тест WebSocket через Python на VM:")
exit_code, output, err = run_cmd(ssh, '''
python3 << 'PYEOF'
import asyncio
import json
import websockets

async def test():
    try:
        uri = "ws://localhost:42002/ws/chat?access_key=megakey1"
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri, close_timeout=10) as ws:
            msg = {"content": "What can you do?"}
            print(f"Sending: {msg}")
            await ws.send(json.dumps(msg))
            print("Waiting for response...")
            response = await asyncio.wait_for(ws.recv(), timeout=60)
            print(f"Response: {response[:500] if len(response) > 500 else response}")
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

result = asyncio.run(test())
print(f"Test {'PASSED' if result else 'FAILED'}")
PYEOF
''', timeout=120)
print(output if output else err)

# Check nanobot logs for message processing
print("\n2. Логи nanobot (последние 20 строк):")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | tail -20")
print(output if output else err)

ssh.close()
