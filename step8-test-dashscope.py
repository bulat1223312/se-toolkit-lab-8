import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30, allow_agent=False, look_for_keys=False)

def run(cmd, timeout=30):
    _, out, err = client.exec_command(cmd, timeout=timeout)
    o = out.read().decode(errors='replace')
    if o: print(o[:2000])
    return o

# Get OAuth token
token = run('python3 -c "import json; print(json.load(open(\'/root/.qwen/oauth_creds.json\'))[\'access_token\'])"').strip()

# Test DashScope with OAuth token
script = f"""import urllib.request, json

token = "{token}"

# Test DashScope with OAuth token
for model in ["qwen-plus", "qwen-max", "qwen-turbo"]:
    data = json.dumps({{'model': model, 'messages': [{{'role': 'user', 'content': 'say ok'}}], 'max_tokens': 5}}).encode()
    req = urllib.request.Request('https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions', data=data, headers={{'Authorization': f'Bearer {{token}}', 'Content-Type': 'application/json'}})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        r = json.loads(resp.read().decode())
        content = r.get('choices', [{{}}])[0].get('message', {{}}).get('content', 'no content')
        print(f'DashScope {{model}}: OK - {{content[:50]}}')
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f'DashScope {{model}}: {{e.code}} - {{body[:150]}}')
    except Exception as e:
        print(f'DashScope {{model}}: Error - {{e}}')
"""

run(f"cat > /tmp/test_dashscope.py << 'PYEOF'\n{script}\nPYEOF")
print("=== Testing DashScope with OAuth token ===")
run("python3 /tmp/test_dashscope.py 2>&1")

# Also check what qwen-code-api uses
print("\n=== Checking qwen-code-api config ===")
run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python -c 'from qwen_code_api.config import settings; print(f\"qwen_api_base={settings.qwen_api_base}\")' 2>&1")

client.close()
