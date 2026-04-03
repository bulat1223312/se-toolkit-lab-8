import subprocess
import sys
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=120):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode(), stderr.read().decode()

# Write script to list all models
script = '''import urllib.request, json

token = json.load(open("/root/.qwen/oauth_creds.json"))["access_token"]

# List all available models
req = urllib.request.Request(
    "https://portal.qwen.ai/v1/models",
    headers={"Authorization": f"Bearer {token}"}
)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode())
    models = [m["id"] for m in data.get("data", [])]
    print(f"Available models ({len(models)}):")
    for m in models[:20]:
        print(f"  - {m}")
except Exception as e:
    print(f"Error: {e}")

# Try with exact model name from settings
req2 = urllib.request.Request(
    "https://portal.qwen.ai/v1/chat/completions",
    data=json.dumps({"model": "qwen3-coder-plus", "messages": [{"role": "user", "content": "say ok"}], "max_tokens": 5}).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
)
try:
    resp = urllib.request.urlopen(req2, timeout=15)
    result = json.loads(resp.read().decode())
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "no content")
    print(f"qwen3-coder-plus: OK - {content[:50]}")
except urllib.error.HTTPError as e:
    print(f"qwen3-coder-plus: {e.code} - {e.read().decode()[:150]}")
except Exception as e:
    print(f"qwen3-coder-plus: Error - {e}")
'''

run(f"cat > /tmp/check_models.py << 'PYEOF'\n{script}\nPYEOF")
out, _ = run("python3 /tmp/check_models.py 2>&1")
print(out)

client.close()
