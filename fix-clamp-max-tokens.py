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

# Check the function definition
print("=== Checking clamp_max_tokens function ===")
out, _ = run("grep -A 10 'def clamp_max_tokens' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py")
print(out)

# Check how it's called
print("\n=== Checking call site ===")
out, _ = run("grep -B 2 -A 2 'clamp_max_tokens' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py")
print(out)

# Fix: The function likely needs a default value or the call needs to pass the value
# Let's see the full context around line 89
print("\n=== Full context around line 89 ===")
out, _ = run("sed -n '80,100p' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py")
print(out)

# Fix the issue - likely need to pass body.get("max_tokens") as argument
out, _ = run("""sed -i 's/max_tokens = clamp_max_tokens(body.get("max_tokens"))/max_tokens = clamp_max_tokens(body.get("max_tokens", None))/' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py""")

# Verify fix
print("\n=== After fix ===")
out, _ = run("sed -n '85,95p' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py")
print(out)

# Rebuild and restart
print("\n=== Rebuilding ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build qwen-code-api 2>&1 | tail -10", timeout=180)
print(out)

print("\n=== Restarting ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d qwen-code-api 2>&1")
print(out)

import time
time.sleep(10)

# Test
print("\n=== Testing ===")
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
api_key = out.strip()

out, _ = run(f"""curl -s -m 15 http://localhost:42005/v1/chat/completions \\
  -H 'Authorization: Bearer {api_key}' \\
  -H 'Content-Type: application/json' \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' 2>&1 | head -5""")
print(f"Response: {out[:300]}")

client.close()
