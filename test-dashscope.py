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

# Check what URL is being used
print("=== API URL Config ===")
out, _ = run("grep -E 'QWEN.*URL|QWEN.*BASE|DASH' /root/se-toolkit-lab-8/.env.docker.secret | head -5")
print(out)

# Check qwen-code-api config
print("\n=== Qwen API Config in Container ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret exec qwen-code-api env 2>&1 | grep -E 'QWEN|DASH' | head -10")
print(out)

# Check logs for actual URL used
print("\n=== Recent Logs with URL info ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api 2>&1 | grep -iE 'url|request|dashscope|error' | tail -15")
print(out)

# Try direct DashScope API test
print("\n=== Testing DashScope Directly ===")
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
api_key = out.strip()

out, _ = run(f"""curl -s -m 15 https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \\
  -H 'Authorization: Bearer {api_key}' \\
  -H 'Content-Type: application/json' \\
  -d '{{"model":"qwen-plus","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' 2>&1 | head -3""")
print(f"Direct DashScope: {out[:300]}")

client.close()
