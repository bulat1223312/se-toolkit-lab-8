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

# Check oauth_creds.json
print("=== OAuth Credentials ===")
out, _ = run("cat ~/.qwen/oauth_creds.json 2>/dev/null")
print(out)

# Check if QWEN_CODE_API_AUTH_USE is correct on VM
print("\n=== VM .env.docker.secret QWEN vars ===")
out, _ = run("grep 'QWEN_CODE_API_AUTH_USE\\|QWEN_CODE_API_KEY' /root/se-toolkit-lab-8/.env.docker.secret")
print(out)

# Check what the container actually gets
print("\n=== Container actual env ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) env 2>&1 | grep -E 'QWEN_CODE_AUTH|QWEN_CODE_API_KEY'")
print(out)

# The issue: QWEN_CODE_API_AUTH_USE=true in .env but container gets false
# Let's check docker-compose.yml for the qwen-code-api service
print("\n=== Docker compose qwen-code-api env section ===")
out, _ = run("grep -A 25 'qwen-code-api:' /root/se-toolkit-lab-8/docker-compose.yml | grep -E 'QWEN|API_KEY|AUTH' | head -10")
print(out)

client.close()
