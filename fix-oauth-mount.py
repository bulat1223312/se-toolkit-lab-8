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

# Check if oauth_creds.json is accessible inside container
print("=== OAuth creds inside container ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) ls -la /root/.qwen/ 2>&1")
print(out)

out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) cat /root/.qwen/oauth_creds.json 2>&1")
print(f"oauth_creds.json: {out[:200]}")

# Check volume mount in compose
print("\n=== Docker compose volume for qwen-code-api ===")
out, _ = run("grep -A 3 'volumes:' /root/se-toolkit-lab-8/docker-compose.yml | grep -A 2 'qwen-code-api' | head -5 || grep -B 10 'qwen-code-api:' /root/se-toolkit-lab-8/docker-compose.yml | grep -A 2 'volumes:'")
print(out)

# Better approach: show the full qwen-code-api service definition
print("\n=== Full qwen-code-api service ===")
out, _ = run("sed -n '/qwen-code-api:/,/^[^ ]/p' /root/se-toolkit-lab-8/docker-compose.yml | head -40")
print(out)

# Check the actual volume mount
print("\n=== Container mounts ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker inspect $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) 2>&1 | grep -A 5 'Mounts' | head -20")
print(out)

# Get the API key and test with correct auth
print("\n=== Get API key ===")
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
api_key = out.strip()
print(f"API Key: {api_key[:20]}...")

# Test with correct API key
print("\n=== Test with correct API key ===")
out, _ = run(f"""curl -s -m 30 http://localhost:42005/v1/chat/completions \\
  -H 'Authorization: Bearer {api_key}' \\
  -H 'Content-Type: application/json' \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' 2>&1""")
print(f"Response: {out[:500]}")

client.close()
