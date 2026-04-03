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

# Stop and remove container completely
print("=== Stopping and removing container ===")
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret stop qwen-code-api 2>&1")
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret rm -f qwen-code-api 2>&1")

time.sleep(3)

# Clear logs
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api > /dev/null 2>&1")

# Start fresh
print("\n=== Starting fresh ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d qwen-code-api 2>&1")
print(out)

time.sleep(15)

# Check fresh startup logs
print("\n=== Fresh startup logs ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api 2>&1 | grep -E 'DEBUG|credentials|Default credentials|No credentials' | head -10")
print(out)

# Test LLM
print("\n=== Testing LLM API ===")
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
api_key = out.strip()

out, _ = run(f"""curl -s -m 30 http://localhost:42005/v1/chat/completions \\
  -H 'Authorization: Bearer {api_key}' \\
  -H 'Content-Type: application/json' \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' 2>&1""")
print(f"Response: {out[:500]}")

# If success, show the full response
if "choices" in out:
    import json
    try:
        data = json.loads(out)
        print(f"\nLLM Response: {data['choices'][0]['message']['content']}")
    except:
        pass

client.close()
