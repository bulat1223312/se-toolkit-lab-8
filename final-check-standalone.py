#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final check - standalone script."""

import subprocess
import sys

# Install paramiko if needed
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko"], capture_output=True)

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    return out, err

print("=" * 60)
print("FINAL TASK 2 VERIFICATION")
print("=" * 60)

# Check services
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps 2>&1")
print("\n--- Services Status ---")
print('\n'.join([l for l in out.split('\n') if 'se-toolkit' in l]))

# Qwen health
out, _ = run("curl -s http://localhost:42005/health 2>&1")
print(f"\n--- Qwen Health ---")
print(out[:150])

# Nanobot key logs
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot 2>&1 | grep -iE 'webchat|connected|channels|agent loop' | tail -10")
print(f"\n--- Nanobot Key Logs ---")
print(out)

# WebSocket test
out, _ = run("""cd /root/se-toolkit-lab-8 && timeout 15 python3 -c "
import asyncio, json, websockets
async def test():
    key = open('.env.docker.secret').read().split('NANOBOT_ACCESS_KEY=')[1].split()[0]
    uri = f'ws://localhost:42002/ws/chat?access_key={key}'
    async with websockets.connect(uri, close_timeout=5) as ws:
        await ws.send(json.dumps({'content': 'Test'}))
        resp = await asyncio.wait_for(ws.recv(), timeout=10)
        print('WS_SUCCESS: ' + resp[:100])
asyncio.run(test())
" 2>&1""")
print(f"\n--- WebSocket Test ---")
print(out[:300] if out else "No response")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)

client.close()
