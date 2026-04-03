import subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30, allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    _, out, err = client.exec_command(cmd, timeout=timeout)
    o = out.read().decode(errors='replace')
    if o: print(o[-2000:] if len(o) > 2000 else o)
    return o, err.read().decode(errors='replace') if err else ''

# Write refresh script to host, then copy to container
script = r'''import httpx, json, time, asyncio

with open('/root/.qwen/oauth_creds.json') as f:
    creds = json.load(f)

print(f"Expires: {creds.get('expiry_date')}")
print(f"Now: {int(time.time() * 1000)}")

async def refresh():
    async with httpx.AsyncClient() as c:
        resp = await c.post(
            'https://chat.qwen.ai/api/v1/oauth2/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': creds['refresh_token'],
                'client_id': 'f0304373b74a44d2b584a3fb70ca9e56',
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            new = {
                'access_token': data['access_token'],
                'token_type': data.get('token_type', 'Bearer'),
                'refresh_token': data.get('refresh_token', creds['refresh_token']),
                'resource_url': data.get('resource_url', ''),
                'expiry_date': int(time.time() * 1000) + data.get('expires_in', 7200) * 1000
            }
            with open('/root/.qwen/oauth_creds.json', 'w') as f:
                json.dump(new, f, indent=2)
            print("Updated!")
            test = await c.post(
                'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
                headers={'Authorization': f"Bearer {new['access_token']}", 'Content-Type': 'application/json'},
                json={'model': 'qwen-plus', 'messages': [{'role': 'user', 'content': 'say ok'}], 'max_tokens': 5}
            )
            print(f"Test: {test.status_code} - {test.text[:200]}")
        else:
            print(f"Failed: {resp.text[:500]}")

asyncio.run(refresh())
'''

# Write to host
with open('/tmp/refresh_qwen.py', 'w') as f:
    f.write(script)

# Copy to container
CONTAINER_CMD = "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps -q qwen-code-api"
out, _ = run(CONTAINER_CMD)
container_id = out.strip()
print(f"Container: {container_id}")

run(f"docker cp /tmp/refresh_qwen.py {container_id}:/tmp/refresh.py")

# Run in container
print("\n=== Refreshing token ===")
run(f"docker exec {container_id} python /tmp/refresh.py 2>&1", timeout=30)

# Copy back to host
print("\n=== Copying creds back ===")
run(f"docker cp {container_id}:/root/.qwen/oauth_creds.json /root/.qwen/oauth_creds.json")
run("chmod 644 /root/.qwen/oauth_creds.json")

# Restart
print("\n=== Restarting qwen-code-api ===")
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart qwen-code-api")
time.sleep(15)

# Test
print("\n=== LLM Test ===")
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
key = out.strip()
out, _ = run(f"curl -s -m 30 http://localhost:42005/v1/chat/completions -H 'Authorization: Bearer {key}' -H 'Content-Type: application/json' -d '{{\"model\":\"coder-model\",\"messages\":[{{\"role\":\"user\",\"content\":\"say ok\"}}],\"max_tokens\":5}}' 2>&1")
print(out[:500])

print("\n=== DONE ===")
client.close()
