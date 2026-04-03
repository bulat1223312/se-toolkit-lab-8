#!/usr/bin/env python3
"""Sync files from VM to local and do final checks."""

import paramiko
import time
import os

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    return out, err

# Get files from VM
files_to_sync = [
    ("nanobot/Dockerfile", "nanobot/Dockerfile"),
    ("nanobot/pyproject.toml", "nanobot/pyproject.toml"),
    ("nanobot/entrypoint.py", "nanobot/entrypoint.py"),
    ("nanobot/config.json", "nanobot/config.json"),
    ("nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml", "nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml"),
    ("nanobot-websocket-channel/mcp-webchat/pyproject.toml", "nanobot-websocket-channel/mcp-webchat/pyproject.toml"),
    ("nanobot-websocket-channel/nanobot-webchat/pyproject.toml", "nanobot-websocket-channel/nanobot-webchat/pyproject.toml"),
]

print("=== Syncing files from VM ===")
for vm_path, local_path in files_to_sync:
    try:
        out, _ = run(f"cat /root/se-toolkit-lab-8/{vm_path}")
        local_full = f"c:\\Users\\user\\se-toolkit-lab-8\\{local_path}"
        os.makedirs(os.path.dirname(local_full), exist_ok=True)
        with open(local_full, 'w', encoding='utf-8') as f:
            f.write(out)
        print(f"✓ {vm_path}")
    except Exception as e:
        print(f"✗ {vm_path}: {e}")

# Get final logs for REPORT.md
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail 50")
with open("c:\\Users\\user\\se-toolkit-lab-8\\nanobot-startup-log.txt", 'w', encoding='utf-8') as f:
    f.write(out)
print("✓ nanobot-startup-log.txt")

# Test WebSocket
out, _ = run("""cd /root/se-toolkit-lab-8 && python3 -c "
import asyncio, json
async def test():
    import websockets
    key = open('.env.docker.secret').read().split('NANOBOT_ACCESS_KEY=')[1].split()[0]
    uri = f'ws://localhost:42002/ws/chat?access_key={key}'
    async with websockets.connect(uri, close_timeout=5) as ws:
        await ws.send(json.dumps({'content': 'Hello'}))
        resp = await asyncio.wait_for(ws.recv(), timeout=30)
        print(resp[:500])
asyncio.run(test())
" 2>&1""")
print(f"\nWebSocket test: {out[:200] if out else 'FAILED'}")

client.close()
