import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30, allow_agent=False, look_for_keys=False)

def run(cmd, timeout=30):
    _, out, err = client.exec_command(cmd, timeout=timeout)
    o = out.read().decode(errors='replace')
    if o: print(o)
    return o

# Get OAuth token
token = run('python3 -c "import json; print(json.load(open(\'/root/.qwen/oauth_creds.json\'))[\'access_token\'])"').strip()
print(f"Token: {token[:30]}...")

# Write test script to VM
script = f"""import urllib.request, json

token = "{token}"

# List models
req = urllib.request.Request('https://portal.qwen.ai/v1/models', headers={{'Authorization': f'Bearer {{token}}'}})
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read().decode())
models = [m['id'] for m in data.get('data', [])]
print(f'Found {{len(models)}} models:')
for m in models[:20]:
    print(f'  - {{m}}')

# Test first available model
if models:
    model = models[0]
    data = json.dumps({{'model': model, 'messages': [{{'role': 'user', 'content': 'say ok'}}], 'max_tokens': 5}}).encode()
    req = urllib.request.Request('https://portal.qwen.ai/v1/chat/completions', data=data, headers={{'Authorization': f'Bearer {{token}}', 'Content-Type': 'application/json'}})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        r = json.loads(resp.read().decode())
        content = r.get('choices', [{{}}])[0].get('message', {{}}).get('content', 'no content')
        print(f'\\nModel {{model}}: OK - {{content[:50]}}')
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f'\\nModel {{model}}: {{e.code}} - {{body[:200]}}')
    except Exception as e:
        print(f'\\nModel {{model}}: Error - {{e}}')
"""

run(f"cat > /tmp/test_models2.py << 'PYEOF'\n{script}\nPYEOF")
print("\n=== Running model test ===")
run("python3 /tmp/test_models2.py 2>&1")

client.close()
