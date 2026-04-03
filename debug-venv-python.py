import subprocess
import sys
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)

import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode(), stderr.read().decode()

# Find the correct python in the container
print("=== Finding python in container ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) which python3 2>&1")
print(f"which python3: {out.strip()}")

out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) ls /app/.venv/bin/python* 2>&1")
print(f"venv python: {out.strip()}")

# Test with the venv python
print("\n=== Test with venv python ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) /app/.venv/bin/python -c 'from qwen_code_api.auth import AuthManager; am=AuthManager(); c=am.load_credentials(); print(f\"creds={c is not None}, token={c.access_token[:20] if c else None}\")' 2>&1")
print(out)

# Also test with venv python importing settings
print("\n=== Test settings with venv python ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) /app/.venv/bin/python -c 'from qwen_code_api.config import settings; from pathlib import Path; print(f\"auth_use={settings.qwen_code_auth_use}, creds_file={settings.creds_file}, home={Path.home()}, exists={settings.creds_file.exists()}\")' 2>&1")
print(out)

# Try reading the file with venv python
print("\n=== Read creds file with venv python ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) /app/.venv/bin/python -c 'from pathlib import Path; p=Path(\"/root/.qwen/oauth_creds.json\"); print(f\"exists={p.exists()}, readable={p.is_file()}\"); print(f\"content={p.read_text()[:100]}\")' 2>&1")
print(out)

# The issue might be that Path.home() in the venv context is different
print("\n=== Check Path.home() in venv ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) /app/.venv/bin/python -c 'from pathlib import Path; print(f\"home={Path.home()}\"); p=Path.home()/\".qwen\"/\"oauth_creds.json\"; print(f\"creds_path={p}, exists={p.exists()}\")' 2>&1")
print(out)

client.close()
