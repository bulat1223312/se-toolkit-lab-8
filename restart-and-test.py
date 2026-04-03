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

# Stop and remove the container completely
print("=== Stopping qwen-code-api ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop qwen-code-api 2>&1")
print(out)

# Remove the container
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret rm -f qwen-code-api 2>&1")
print(out)

# Wait a moment
time.sleep(3)

# Start fresh
print("\n=== Starting fresh ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d qwen-code-api 2>&1")
print(out)

# Wait for startup
print("\nWaiting for startup...")
time.sleep(15)

# Check startup logs
print("\n=== Startup logs ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api 2>&1 | grep -v opentelemetry")
print(out)

# Get API key
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
api_key = out.strip()

# Test the API
print("\n=== Testing LLM API ===")
out, _ = run(f"""curl -s -m 30 http://localhost:42005/v1/chat/completions \\
  -H 'Authorization: Bearer {api_key}' \\
  -H 'Content-Type: application/json' \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' 2>&1""")
print(f"Response: {out[:500]}")

# Check error logs if failed
if "Internal Server Error" in out or "error" in out.lower():
    print("\n=== Error logs ===")
    out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api 2>&1 | grep -iE 'error|traceback|exception|credentials' | tail -10")
    print(out)

client.close()
