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

# Write script to VM directly
print("=== Writing test script to VM ===")
run('cat > /tmp/test_portal.py << \'PYEOF\'\nimport urllib.request, json\n\ntoken = json.load(open("/root/.qwen/oauth_creds.json"))["access_token"]\nprint(f"Token: {token[:30]}...")\n\ndata = json.dumps({"model": "qwen-turbo", "messages": [{"role": "user", "content": "say ok"}], "max_tokens": 5}).encode()\nreq = urllib.request.Request(\n    "https://portal.qwen.ai/v1/chat/completions",\n    data=data,\n    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}\n)\ntry:\n    resp = urllib.request.urlopen(req, timeout=15)\n    print(f"Status: {resp.status}")\n    print(f"Body: {resp.read().decode()[:300]}")\nexcept urllib.error.HTTPError as e:\n    print(f"Status: {e.code}")\n    print(f"Body: {e.read().decode()[:300]}")\nexcept Exception as e:\n    print(f"Error: {e}")\nPYEOF')

# Verify and run
out, _ = run("ls -la /tmp/test_portal.py && python3 /tmp/test_portal.py 2>&1")
print(out)

client.close()
