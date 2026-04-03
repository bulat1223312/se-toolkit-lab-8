import paramiko
import sys

# Install paramiko
import subprocess
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode(), stderr.read().decode()

print("=== Syncing files from VM ===")

files = [
    "nanobot-websocket-channel/mcp-webchat/pyproject.toml",
    "nanobot-websocket-channel/nanobot-webchat/pyproject.toml",
    "nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml",
    "nanobot/Dockerfile",
    "nanobot/entrypoint.py",
    "nanobot/config.json",
    "nanobot/pyproject.toml",
]

for f in files:
    out, _ = run(f"cat /root/se-toolkit-lab-8/{f}")
    path = f"c:\\Users\\user\\se-toolkit-lab-8\\{f}"
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fp:
        fp.write(out.encode('utf-8', errors='replace'))
    print(f"✓ {f}")

# Final verification
print("\n=== Final Verification ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps 2>&1")
print("\nServices:")
for line in out.split('\n'):
    if 'nanobot' in line or 'qwen' in line or 'caddy' in line:
        print(f"  {line}")

out, _ = run("curl -s http://localhost:42005/health 2>&1")
print(f"\nQwen Health: {out[:100] if out else 'FAILED'}")

out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot 2>&1 | grep -iE 'webchat|connected|channels|agent' | tail -8")
print(f"\nNanobot Status:")
print(out)

# WebSocket test
out, _ = run("""cd /root/se-toolkit-lab-8 && timeout 15 python3 -c "
import asyncio, json, websockets
async def test():
    key = open('.env.docker.secret').read().split('NANOBOT_ACCESS_KEY=')[1].split()[0]
    uri = f'ws://localhost:42002/ws/chat?access_key={key}'
    async with websockets.connect(uri, close_timeout=5) as ws:
        await ws.send(json.dumps({'content': 'Hello'}))
        resp = await asyncio.wait_for(ws.recv(), timeout=10)
        print('SUCCESS: ' + resp[:100])
asyncio.run(test())
" 2>&1""")
print(f"\nWebSocket Test: {out[:200] if out else 'FAILED'}")

print("\n=== DONE ===")
client.close()
