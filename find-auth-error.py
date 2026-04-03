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

# Find the exact error message in the codebase
print("=== Finding 'Authentication failed' error ===")
out, _ = run("grep -r 'Authentication failed' /root/se-toolkit-lab-8/qwen-code-api/src/ 2>/dev/null")
print(out)

# Check the validate_api_key function
print("\n=== validate_api_key function ===")
out, _ = run("grep -A 30 'def validate_api_key' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/main.py")
print(out)

# Check config for api_keys
print("\n=== api_keys config ===")
out, _ = run("grep -E 'api_keys|API_KEYS|QWEN_CODE_API_KEY' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/config.py")
print(out)

# Check what the container sees for api_keys
print("\n=== Container api_keys ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python -c 'from qwen_code_api.config import settings; print(f\"api_keys={settings.api_keys}\")' 2>&1")
print(out)

# Check env vars in container
print("\n=== Container QWEN env vars ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) env 2>&1 | grep QWEN")
print(out)

client.close()
