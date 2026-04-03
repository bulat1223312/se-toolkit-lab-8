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

# Get the OAuth access token
print("=== Getting OAuth token ===")
out, _ = run("python3 -c \"import json; print(json.load(open('/root/.qwen/oauth_creds.json'))['access_token'])\" 2>&1")
access_token = out.strip()
print(f"Token: {access_token[:30]}...")

# Test the token directly against DashScope
print("\n=== Testing OAuth token against DashScope ===")
cmd = f"""curl -s -m 15 https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \\
  -H 'Authorization: Bearer {access_token}' \\
  -H 'Content-Type: application/json' \\
  -d '{{"model":"qwen-plus","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' 2>&1"""
out, _ = run(cmd)
print(f"DashScope response: {out[:500]}")

# Check is_auth_error function
print("\n=== is_auth_error function ===")
out, _ = run("grep -A 20 'def is_auth_error' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/models.py")
print(out)

# Check what DashScope returns for auth errors
print("\n=== Check qwen_api_base setting ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python -c 'from qwen_code_api.config import settings; print(f\"qwen_api_base={settings.qwen_api_base}\")' 2>&1")
print(out)

client.close()
