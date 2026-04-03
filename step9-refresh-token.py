import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30, allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    _, out, err = client.exec_command(cmd, timeout=timeout)
    o = out.read().decode(errors='replace')
    if o: print(o[:2000])
    return o

# Refresh OAuth token using qwen-code-api's refresh endpoint
script = """import httpx, json, time

# Load current creds
with open('/root/.qwen/oauth_creds.json') as f:
    creds = json.load(f)

print(f"Current token expires: {creds.get('expiry_date')}")
print(f"Current time (ms): {int(time.time() * 1000)}")

# Refresh token
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
            print(f"New token: {data.get('access_token', '')[:30]}...")
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
            # Now test
            test_resp = await c.post(
                'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
                headers={'Authorization': f"Bearer {new_creds['access_token']}", 'Content-Type': 'application/json'},
                json={'model': 'qwen-plus', 'messages': [{'role': 'user', 'content': 'say ok'}], 'max_tokens': 5}
            )
            print(f"Test status: {test_resp.status_code}")
            print(f"Test body: {test_resp.text[:300]}")
        else:
            print(f"Refresh failed: {resp.text[:300]}")

import asyncio
asyncio.run(refresh())
"""

run(f"cat > /tmp/refresh_token.py << 'PYEOF'\n{script}\nPYEOF")
print("=== Refreshing OAuth token ===")
# Use system python with httpx
run("pip install httpx -q 2>&1")
run("python3 /tmp/refresh_token.py 2>&1")

print("\n=== DONE ===")
client.close()
