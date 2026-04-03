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

# Fix file permissions on the host
print("=== Fixing file permissions ===")
run("chmod 644 /root/.qwen/oauth_creds.json")
out, _ = run("ls -la /root/.qwen/oauth_creds.json")
print(f"Permissions: {out.strip()}")

# Restart container to pick up new permissions
print("\n=== Restarting qwen-code-api ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart qwen-code-api 2>&1")
print(out)

time.sleep(15)

# Check startup logs
print("\n=== Startup logs after permission fix ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api 2>&1 | grep -E 'DEBUG|credentials|Default credentials' | head -10")
print(out)

# Test LLM API
print("\n=== Testing LLM API ===")
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
api_key = out.strip()

out, _ = run(f"""curl -s -m 30 http://localhost:42005/v1/chat/completions \\
  -H 'Authorization: Bearer {api_key}' \\
  -H 'Content-Type: application/json' \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' 2>&1""")
print(f"Response: {out[:500]}")

# If still failing, check error logs
if "Internal Server Error" in out or not out.strip():
    print("\n=== Error logs ===")
    out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api 2>&1 | grep -iE 'error|traceback|exception|credentials' | tail -10")
    print(out)

client.close()
