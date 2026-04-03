import subprocess
import sys
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode(), stderr.read().decode()

# Get OAuth token
out, _ = run("python3 -c \"import json; print(json.load(open('/root/.qwen/oauth_creds.json'))['access_token'])\" 2>&1")
access_token = out.strip()
print(f"OAuth Token: {access_token[:30]}...")

# Test with different models on portal.qwen.ai
for model in ["qwen-turbo", "qwen-plus", "qwen-max"]:
    print(f"\n=== Testing model: {model} ===")
    test_script = f"""
import urllib.request, json
token = "{access_token}"
data = json.dumps({{"model": "{model}", "messages": [{{"role": "user", "content": "say ok"}}], "max_tokens": 5}}).encode()
req = urllib.request.Request(
    "https://portal.qwen.ai/v1/chat/completions",
    data=data,
    headers={{"Authorization": f"Bearer {{token}}", "Content-Type": "application/json"}}
)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    print(f"Status: {{resp.status}}")
    print(f"Body: {{resp.read()[:200]}}")
except urllib.error.HTTPError as e:
    print(f"Status: {{e.code}}")
    print(f"Body: {{e.read()[:200]}}")
except Exception as e:
    print(f"Error: {{e}}")
"""
    out, _ = run(f'python3 -c "{test_script}" 2>&1')
    print(out)

# Also try DashScope with OAuth token
print("\n=== Testing DashScope with OAuth token ===")
test_script = f"""
import urllib.request, json
token = "{access_token}"
data = json.dumps({{"model": "qwen-plus", "messages": [{{"role": "user", "content": "say ok"}}], "max_tokens": 5}}).encode()
req = urllib.request.Request(
    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    data=data,
    headers={{"Authorization": f"Bearer {{token}}", "Content-Type": "application/json"}}
)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    print(f"Status: {{resp.status}}")
    print(f"Body: {{resp.read()[:200]}}")
except urllib.error.HTTPError as e:
    print(f"Status: {{e.code}}")
    print(f"Body: {{e.read()[:200]}}")
except Exception as e:
    print(f"Error: {{e}}")
"""
out, _ = run(f'python3 -c "{test_script}" 2>&1')
print(out)

client.close()
