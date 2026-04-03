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

# Write test script to container
script = r'''
from pathlib import Path
from pydantic import BaseModel
import json

class QwenCredentials(BaseModel):
    access_token: str = ""
    refresh_token: str = ""
    token_type: str = ""
    resource_url: str = ""
    expiry_date: int = 0

creds_path = Path.home() / ".qwen" / "oauth_creds.json"
print(f"creds_file: {creds_path}")
print(f"exists: {creds_path.exists()}")
if creds_path.exists():
    content = creds_path.read_text()
    print(f"content length: {len(content)}")
    print(f"raw content: {content[:100]}")
    try:
        creds = QwenCredentials.model_validate_json(content)
        print(f"Parsed OK: token_type={creds.token_type}, expiry={creds.expiry_date}")
    except Exception as e:
        print(f"Parse error: {type(e).__name__}: {e}")

# Also try standard json
try:
    data = json.loads(content)
    print(f"JSON parse OK: keys={list(data.keys())}")
except Exception as e:
    print(f"JSON parse error: {e}")
'''

# Write to container's /tmp
run(f'cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) bash -c "cat > /tmp/test_creds.py" <<< "{script}" 2>&1')

# Verify it was written
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) head -5 /tmp/test_creds.py 2>&1")
print(f"Script written: {out[:100]}")

# Run it
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python3 /tmp/test_creds.py 2>&1")
print(f"\nTest result:\n{out}")

client.close()
