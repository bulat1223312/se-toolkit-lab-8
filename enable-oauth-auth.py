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

# Check token expiry
import json
out, _ = run("cat ~/.qwen/oauth_creds.json")
creds = json.loads(out)
expiry_ms = creds.get('expiry_date', 0)
expiry_s = expiry_ms / 1000
import datetime
expiry_dt = datetime.datetime.fromtimestamp(expiry_s, tz=datetime.timezone.utc)
now = datetime.datetime.now(tz=datetime.timezone.utc)
print(f"Token expires: {expiry_dt}")
print(f"Current time: {now}")
print(f"Token valid: {expiry_dt > now}")

# Fix .env.docker.secret - set QWEN_CODE_API_AUTH_USE=true
print("\n=== Enabling OAuth auth ===")
run("""sed -i 's/QWEN_CODE_API_AUTH_USE=false/QWEN_CODE_API_AUTH_USE=true/' /root/se-toolkit-lab-8/.env.docker.secret""")

# Verify
out, _ = run("grep 'QWEN_CODE_API_AUTH_USE' /root/se-toolkit-lab-8/.env.docker.secret")
print(f"New value: {out.strip()}")

# Recreate qwen-code-api container to pick up new env
print("\n=== Recreating qwen-code-api ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d --force-recreate qwen-code-api 2>&1")
print(out)

import time
time.sleep(15)

# Check container env
print("\n=== Container env after restart ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) env 2>&1 | grep -E 'QWEN_CODE_AUTH|QWEN_CODE_API_KEY'")
print(out)

# Check logs
print("\n=== Recent logs ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api --tail 20 2>&1 | grep -v opentelemetry")
print(out)

# Test the API
print("\n=== Testing LLM API ===")
out, _ = run("""curl -s -m 30 http://localhost:42005/v1/chat/completions \\
  -H 'Authorization: Bearer placeholder' \\
  -H 'Content-Type: application/json' \\
  -d '{"model":"coder-model","messages":[{"role":"user","content":"say ok"}],"max_tokens":5}' 2>&1""")
print(f"Response: {out[:500]}")

client.close()
