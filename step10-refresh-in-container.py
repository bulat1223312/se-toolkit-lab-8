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
    return o

CONTAINER = "$(cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps -q qwen-code-api)"

# Refresh token using container's venv python
script = """
import httpx, json, time, asyncio

with open('/root/.qwen/oauth_creds.json') as f:
    creds = json.load(f)

print(f"Current token expires: {creds.get('expiry_date')}")
print(f"Current time (ms): {int(time.time() * 1000)}")

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
        print(f"Refresh status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            new_creds = {
                'access_token': data['access_token'],
                'token_type': data.get('token_type', 'Bearer'),
                'refresh_token': data.get('refresh_token', creds['refresh_token']),
                'resource_url': data.get('resource_url', creds.get('resource_url', '')),
                'expiry_date': int(time.time() * 1000) + data.get('expires_in', 7200) * 1000
            }
            with open('/root/.qwen/oauth_creds.json', 'w') as f:
                json.dump(new_creds, f, indent=2)
            print("Credentials updated!")
            # Test with DashScope
            test = await c.post(
                'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
                headers={'Authorization': f"Bearer {new_creds['access_token']}", 'Content-Type': 'application/json'},
                json={'model': 'qwen-plus', 'messages': [{'role': 'user', 'content': 'say ok'}], 'max_tokens': 5}
            )
            print(f"DashScope test: {test.status_code} - {test.text[:300]}")
        else:
            print(f"Refresh failed: {resp.text[:500]}")

asyncio.run(refresh())
"""

# Write script inside container
run(f"docker exec {CONTAINER} bash -c \"cat > /tmp/refresh.py << 'PYEOF'\n{script}\nPYEOF\"")

# Run it
print("=== Refreshing OAuth token inside container ===")
run(f"docker exec {CONTAINER} python /tmp/refresh.py 2>&1", timeout=30)

# Copy updated creds to host
print("\n=== Copying updated creds to host ===")
run(f"docker cp $(cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps -q qwen-code-api):/root/.qwen/oauth_creds.json /root/.qwen/oauth_creds.json 2>&1")
run("chmod 644 /root/.qwen/oauth_creds.json")

# Restart qwen-code-api
print("\n=== Restarting qwen-code-api ===")
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart qwen-code-api 2>&1")
time.sleep(15)

# Test LLM
print("\n=== LLM Test ===")
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
key = out.strip()
run(f"curl -s -m 30 http://localhost:42005/v1/chat/completions -H 'Authorization: Bearer {key}' -H 'Content-Type: application/json' -d '{{\"model\":\"coder-model\",\"messages\":[{{\"role\":\"user\",\"content\":\"say ok\"}}],\"max_tokens\":5}}' 2>&1")

print("\n=== DONE ===")
client.close()
