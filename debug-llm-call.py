import subprocess
import sys
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)

import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode(), stderr.read().decode()

# Clear logs
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api > /dev/null 2>&1")

# Get API key
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
api_key = out.strip()

# Make request
print("=== Making LLM request ===")
out, _ = run(f"""curl -s -m 30 http://localhost:42005/v1/chat/completions \\
  -H 'Authorization: Bearer {api_key}' \\
  -H 'Content-Type: application/json' \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' 2>&1""")
print(f"Response: {out[:500]}")

# Check logs immediately
time.sleep(2)
print("\n=== Qwen logs after request (errors only) ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api 2>&1 | grep -iE 'error|traceback|exception|failed' | tail -20")
print(out)

# Check if qwen-code-api can read creds
print("\n=== Qwen config check ===")
check_script = """
from pathlib import Path
import json
p = Path.home() / '.qwen' / 'oauth_creds.json'
print(f'Creds path: {p}')
print(f'Exists: {p.exists()}')
if p.exists():
    creds = json.loads(p.read_text())
    print(f'Token type: {creds.get("token_type")}')
    print(f'Expiry: {creds.get("expiry_date")}')
"""
cmd = f'cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python3 -c "{check_script}" 2>&1'
out, _ = run(cmd)
print(out)

client.close()
