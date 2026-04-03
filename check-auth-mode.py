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

# Check auth config
print("=== Auth Config ===")
out, _ = run("grep -E 'QWEN_CODE_AUTH|QWEN_CODE_API_KEY' /root/se-toolkit-lab-8/.env.docker.secret")
print(out)

# Check how auth is handled in code
print("\n=== Auth Check in Code ===")
out, _ = run("grep -A 20 'def validate_api_key' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/main.py 2>/dev/null || grep -r 'validate_api_key' /root/se-toolkit-lab-8/qwen-code-api/src/ | head -5")
print(out)

# Check if there's a simpler auth mode
print("\n=== Looking for direct API key mode ===")
out, _ = run("grep -r 'QWEN_CODE_AUTH_USE' /root/se-toolkit-lab-8/qwen-code-api/src/ | head -10")
print(out)

# Show the chat route auth handling
print("\n=== Chat route auth ===")
out, _ = run("grep -B 5 -A 15 'qwen_code_auth_use' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py | head -40")
print(out)

client.close()
