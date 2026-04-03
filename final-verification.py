#!/usr/bin/env python3
"""Final comprehensive check of Task 2."""

import paramiko
import time

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

# 1. Check all services are running
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps")
print("\n--- Services Status ---")
for line in out.split('\n'):
    if 'se-toolkit' in line:
        print(line)

# 2. Check qwen-code-api health
out, _ = run("curl -s http://localhost:42005/health")
print(f"\n--- Qwen Code API Health ---")
print(out[:200] if out else "FAILED")

# 3. Check nanobot logs for successful startup
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail 20")
print("\n--- Nanobot Recent Logs ---")
for line in out.split('\n'):
    if any(k in line for k in ['WebChat', 'connected', 'Agent loop', 'channels']):
        print(line)

# 4. Check Flutter build
out, _ = run("docker volume inspect se-toolkit-lab-8_client-web-flutter 2>&1 | head -5")
print(f"\n--- Flutter Volume ---")
print("✓ Volume exists" if "client-web-flutter" in out else "✗ Volume missing")

# 5. Check Caddy routes
out, _ = run("grep -E 'flutter|ws/chat' /root/se-toolkit-lab-8/caddy/Caddyfile")
print(f"\n--- Caddy Routes ---")
print(out)

# 6. Test WebSocket (quick test)
out, _ = run("""cd /root/se-toolkit-lab-8 && timeout 10 python3 -c "
import asyncio, json, websockets
async def test():
    key = open('.env.docker.secret').read().split('NANOBOT_ACCESS_KEY=')[1].split()[0]
    uri = f'ws://localhost:42002/ws/chat?access_key={key}'
    async with websockets.connect(uri, close_timeout=5) as ws:
        await ws.send(json.dumps({'content': 'Test'}))
        resp = await asyncio.wait_for(ws.recv(), timeout=8)
        print('SUCCESS: ' + resp[:100])
asyncio.run(test())
" 2>&1""")
print(f"\n--- WebSocket Test ---")
print(out[:200] if out else "FAILED or timeout")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)

client.close()
