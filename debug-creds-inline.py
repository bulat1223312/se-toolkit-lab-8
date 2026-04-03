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

# Use docker exec with a simpler approach - run inline python
print("=== Testing creds parsing inline ===")
cmd = """cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python3 -c '
from pathlib import Path
from pydantic import BaseModel
import json

class QC(BaseModel):
    access_token: str = ""
    refresh_token: str = ""
    token_type: str = ""
    resource_url: str = ""
    expiry_date: int = 0

p = Path.home() / ".qwen" / "oauth_creds.json"
print(f"path={p} exists={p.exists()}")
if p.exists():
    c = p.read_text()
    print(f"len={len(c)} first100={c[:100]}")
    try:
        q = QC.model_validate_json(c)
        print(f"OK: tt={q.token_type} exp={q.expiry_date}")
    except Exception as e:
        print(f"ERR: {type(e).__name__}: {e}")
    try:
        d = json.loads(c)
        print(f"json OK: keys={list(d.keys())}")
    except Exception as e:
        print(f"json ERR: {e}")
' 2>&1"""

out, _ = run(cmd)
print(out)

# Also check what the actual config settings look like
print("\n=== Check config settings ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python3 -c 'from qwen_code_api.config import settings; print(f\"auth_use={settings.qwen_code_auth_use} creds={settings.creds_file}\")' 2>&1")
print(out)

# Check the actual error in the code path
print("\n=== Check if the issue is in the code path ===")
# The error "No credentials found" comes from auth.py when load_credentials returns None
# But we know the file exists and is readable. Let's check if settings.qwen_code_auth_use is actually True in the running app
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python3 -c 'import os; print(f\"QWEN_CODE_AUTH_USE={os.environ.get(\"QWEN_CODE_AUTH_USE\")}\")' 2>&1")
print(out)

client.close()
