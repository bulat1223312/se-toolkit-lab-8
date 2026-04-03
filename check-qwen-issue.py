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

# Check Qwen Code API logs for errors
print("=== Qwen Code API Recent Logs ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api --tail 30 2>&1")
print(out)

# Check if Qwen API key is set
print("\n=== Qwen API Key Check ===")
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | head -3")
print(out)

# Check Qwen auth config
print("\n=== Qwen Auth Config ===")
out, _ = run("grep QWEN_CODE_AUTH /root/se-toolkit-lab-8/.env.docker.secret")
print(out)

# Test Qwen API directly
print("\n=== Direct Qwen API Test ===")
out, _ = run("""curl -s -m 10 http://localhost:42005/v1/chat/completions \\
  -H 'X-API-Key: $(grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d "[:space:]")' \\
  -H 'Content-Type: application/json' \\
  -d '{"model":"coder-model","messages":[{"role":"user","content":"say ok"}],"max_tokens":5}' 2>&1 | head -5""")
print(out[:500] if out else "FAILED")

client.close()
