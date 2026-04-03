#!/usr/bin/env python3
"""Final check of nanobot status."""

import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    print(f"\n--- {cmd[:70]} ---")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out)
    if err: print(f"STDERR: {err}")
    return out, err

# Check status
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps")

# Check nanobot logs
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail 100")

# Check qwen-code-api health
run("curl -s http://localhost:42005/health")

# Test WebSocket
run("""cd /root/se-toolkit-lab-8 && python3 -c "
import asyncio, json, os
async def test():
    try:
        import websockets
        key = open('.env.docker.secret').read().split('NANOBOT_ACCESS_KEY=')[1].split()[0]
        uri = f'ws://localhost:42002/ws/chat?access_key={key}'
        print(f'Connecting to {{uri[:50]}}...')
        async with websockets.connect(uri, close_timeout=5) as ws:
            await ws.send(json.dumps({'content': 'Hello'}))
            resp = await asyncio.wait_for(ws.recv(), timeout=30)
            print(f'Response: {{resp[:200]}}')
    except Exception as e:
        print(f'Error: {{e}}')
asyncio.run(test())
" 2>&1 || echo 'WS test skipped'""")

client.close()
