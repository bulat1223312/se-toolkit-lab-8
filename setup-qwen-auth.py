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

# Check if qwen CLI is installed
print("=== Checking qwen CLI ===")
out, _ = run("which qwen 2>/dev/null || echo 'not found'")
print(f"qwen location: {out.strip()}")

# Check qwen version
if 'not found' not in out:
    out, _ = run("qwen --version 2>&1")
    print(f"qwen version: {out.strip()}")

# Check existing qwen credentials
print("\n=== Checking existing credentials ===")
out, _ = run("ls -la ~/.qwen/ 2>/dev/null || echo 'no .qwen dir'")
print(out)

out, _ = run("cat ~/.qwen/settings.json 2>/dev/null | head -30 || echo 'no settings.json'")
print(f"settings.json:\n{out}")

# Check for auth files
print("\n=== Checking auth files ===")
out, _ = run("find ~/.qwen -name '*.json' -o -name 'auth*' 2>/dev/null | head -10")
print(out)

out, _ = run("ls -la ~/.dashscope/ 2>/dev/null || echo 'no .dashscope dir'")
print(out)

# Check what the qwen-code-api expects
print("\n=== Qwen Code API auth config ===")
out, _ = run("grep -r 'credentials\\|auth\\|API_KEY' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/config.py 2>/dev/null | head -20")
print(out)

# Check the docker-compose env for qwen-code-api
print("\n=== Docker compose qwen env vars ===")
out, _ = run("grep -A 20 'qwen-code-api:' /root/se-toolkit-lab-8/docker-compose.yml | grep -E 'QWEN|API' | head -10")
print(out)

# Try to login with qwen
print("\n=== Attempting qwen login ===")
out, _ = run("qwen login --help 2>&1 | head -20")
print(out)

client.close()
