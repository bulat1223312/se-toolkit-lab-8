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

# Write the model test script directly to VM
script = '''import urllib.request, json

token = json.load(open("/root/.qwen/oauth_creds.json"))["access_token"]

# Test each model
for model in ["qwen-plus", "qwen-max", "qwen-long", "qwq-plus", "qwq-max"]:
    data = json.dumps({"model": model, "messages": [{"role": "user", "content": "say ok"}], "max_tokens": 5}).encode()
    req = urllib.request.Request(
        "https://portal.qwen.ai/v1/chat/completions",
        data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read().decode())
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "no content")
        print(f"{model}: OK - {content[:50]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"{model}: {e.code} - {body[:100]}")
    except Exception as e:
        print(f"{model}: Error - {e}")
'''

# Write to VM
run(f"cat > /tmp/list_models.py << 'PYEOF'\n{script}\nPYEOF")

# Run on VM
out, _ = run("python3 /tmp/list_models.py 2>&1")
print("=== Available models test ===")
print(out)

client.close()
