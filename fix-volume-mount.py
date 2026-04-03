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

# Check what user the container runs as
print("=== Container user ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) whoami 2>&1")
print(f"User: {out.strip()}")

out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) echo $HOME 2>&1")
print(f"HOME: {out.strip()}")

# Check docker-compose.yml for the volume mount
print("\n=== Docker compose volume for qwen-code-api ===")
out, _ = run("grep -A 30 'qwen-code-api:' /root/se-toolkit-lab-8/docker-compose.yml | grep -B 2 -A 2 'volumes:\\|\\.qwen'")
print(out)

# Fix: change volume mount from ~/.qwen:/root/.qwen to ~/.qwen:/home/nonroot/.qwen
print("\n=== Fixing volume mount ===")
run("sed -i 's|~/.qwen:/root/.qwen:ro|~/.qwen:/home/nonroot/.qwen:ro|' /root/se-toolkit-lab-8/docker-compose.yml")

# Verify fix
out, _ = run("grep '\\.qwen' /root/se-toolkit-lab-8/docker-compose.yml")
print(f"Fixed volume: {out.strip()}")

# Rebuild and restart
print("\n=== Rebuilding ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d --force-recreate qwen-code-api 2>&1")
print(out)

import time
time.sleep(15)

# Check startup logs
print("\n=== Startup logs after fix ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api 2>&1 | grep -E 'DEBUG|credentials|No credentials' | head -10")
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

client.close()
