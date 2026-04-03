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
print(f"Response: {out[:300]}")

# Check logs for the actual URL used
time.sleep(2)
print("\n=== Logs showing URL ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api 2>&1 | grep -iE 'url|request|httpx|dashscope|portal' | tail -10")
print(out)

# Check what get_api_endpoint returns
print("\n=== Check API endpoint ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python -c 'from qwen_code_api.auth import AuthManager; from qwen_code_api.config import settings; am=AuthManager(); creds=am.load_credentials(); print(f\"resource_url={creds.resource_url if creds else None}\"); print(f\"api_endpoint={AuthManager.get_api_endpoint(creds)}\")' 2>&1")
print(out)

# Check the live_logger for request URL
print("\n=== Full recent logs ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api 2>&1 | grep -v opentelemetry | tail -30")
print(out)

client.close()
