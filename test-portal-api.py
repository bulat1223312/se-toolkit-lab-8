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

# Get fresh OAuth token
print("=== Getting fresh OAuth token ===")
out, _ = run("python3 -c \"import json; print(json.load(open('/root/.qwen/oauth_creds.json'))['access_token'])\" 2>&1")
access_token = out.strip()
print(f"Token: {access_token[:30]}...")

# Test direct request to portal.qwen.ai with verbose output
print("\n=== Testing portal.qwen.ai directly ===")
test_script = f"""import httpx, json
async def test():
    token = "{access_token}"
    async with httpx.AsyncClient() as c:
        r = await c.post(
            "https://portal.qwen.ai/v1/chat/completions",
            headers={{"Authorization": f"Bearer {{token}}", "Content-Type": "application/json"}},
            json={{"model": "coder-model", "messages": [{{"role": "user", "content": "say ok"}}], "max_tokens": 5}}
        )
        print(f"Status: {{r.status_code}}")
        print(f"Response: {{r.text[:500]}}")
import asyncio
asyncio.run(test())
"""
run(f'cat > /tmp/test_portal.py << "HEREDOC"\n{test_script}\nHEREDOC')
out, _ = run("python3 /tmp/test_portal.py 2>&1")
print(out)

client.close()
