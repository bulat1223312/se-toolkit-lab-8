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

# Fix the call to pass model as first argument
print("=== Fixing clamp_max_tokens call ===")
out, _ = run("""sed -i 's/max_tokens = clamp_max_tokens(body.get("max_tokens", None))/max_tokens = clamp_max_tokens(model, body.get("max_tokens", 8192))/' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py""")

# Verify
print("\n=== After fix ===")
out, _ = run("grep -A 2 'clamp_max_tokens' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py | head -5")
print(out)

# Rebuild
print("\n=== Rebuilding ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build qwen-code-api 2>&1 | tail -5", timeout=180)
print(out)

# Restart
print("\n=== Restarting ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d qwen-code-api 2>&1")
print(out)

import time
time.sleep(10)

# Test
print("\n=== Testing LLM ===")
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
api_key = out.strip()

out, _ = run(f"""curl -s -m 30 http://localhost:42005/v1/chat/completions \\
  -H 'Authorization: Bearer {api_key}' \\
  -H 'Content-Type: application/json' \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' 2>&1""")
print(f"Response: {out[:500]}")

# Also test without max_tokens
print("\n=== Testing without max_tokens ===")
out, _ = run(f"""curl -s -m 30 http://localhost:42005/v1/chat/completions \\
  -H 'Authorization: Bearer {api_key}' \\
  -H 'Content-Type: application/json' \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"say ok"}}]}}' 2>&1""")
print(f"Response: {out[:500]}")

client.close()
