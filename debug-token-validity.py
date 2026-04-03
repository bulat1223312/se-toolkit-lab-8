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

# Check time in container vs token expiry
print("=== Time check ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python3 -c 'import time; print(f\"container_time_ms={int(time.time()*1000)}\")' 2>&1")
print(out)

# Check token expiry
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python3 -c 'import json,time; c=json.load(open(\"/root/.qwen/oauth_creds.json\")); print(f\"expiry_ms={c[\"expiry_date\"]}\"); print(f\"now_ms={int(time.time()*1000)}\"); print(f\"valid={int(time.time()*1000) < c[\"expiry_date\"]}\")' 2>&1")
print(out)

# Check token_refresh_buffer_s setting
print("\n=== Check token_refresh_buffer_s ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python3 -c 'from qwen_code_api.config import settings; print(f\"token_refresh_buffer_s={settings.token_refresh_buffer_s}\")' 2>&1")
print(out)

# Check config.py for default value
print("\n=== token_refresh_buffer_s default ===")
out, _ = run("grep -E 'token_refresh_buffer|REFRESH_BUFFER' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/config.py")
print(out)

# Now let's trace the actual issue - the AuthManager instance might have cached None
# Let's check what happens when we import auth and call load_credentials
print("\n=== Test AuthManager.load_credentials ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python3 -c 'from qwen_code_api.auth import AuthManager; am=AuthManager(); creds=am.load_credentials(); print(f\"creds={creds is not None}, type={type(creds)}\"); print(f\"access_token={creds.access_token[:20] if creds else None}...\")' 2>&1")
print(out)

client.close()
