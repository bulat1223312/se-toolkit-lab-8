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

# Get API key
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
api_key = out.strip()
print(f"API Key: {api_key[:20]}...")

# Test with Authorization header
print("\n=== Test with Authorization: Bearer ===")
out, _ = run(f"""curl -s -m 10 http://localhost:42005/v1/chat/completions \\
  -H 'Authorization: Bearer {api_key}' \\
  -H 'Content-Type: application/json' \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' 2>&1 | head -3""")
print(out[:300] if out else "FAILED")

# Test with X-API-Key header
print("\n=== Test with X-API-Key ===")
out, _ = run(f"""curl -s -m 10 http://localhost:42005/v1/chat/completions \\
  -H 'X-API-Key: {api_key}' \\
  -H 'Content-Type: application/json' \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' 2>&1 | head -3""")
print(out[:300] if out else "FAILED")

# Check qwen-code-api auth configuration
print("\n=== Qwen Code API Env ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret exec qwen-code-api env 2>&1 | grep -E 'QWEN|AUTH|API_KEY' | head -10")
print(out)

client.close()
