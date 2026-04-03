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

# Check creds inside container more carefully
print("=== Checking creds file permissions ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) ls -la /root/.qwen/oauth_creds.json")
print(out)

# Try reading the file
print("=== Reading creds ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python3 -c \"from pathlib import Path; p=Path('/root/.qwen/oauth_creds.json'); print(f'exists={p.exists()}, size={p.stat().st_size}')\" 2>&1")
print(out)

# Check settings.creds_file value
print("=== Checking settings.creds_file ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python3 -c \"from qwen_code_api.config import settings; from pathlib import Path; print(f'creds_file={settings.creds_file}, auth_use={settings.qwen_code_auth_use}, home={Path.home()}')\" 2>&1")
print(out)

# Try the exact same code as AuthManager
print("\n=== Simulating AuthManager.load_credentials ===")
script = """
from pathlib import Path
from pydantic import BaseModel

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
    try:
        creds = QwenCredentials.model_validate_json(content)
        print(f"Parsed OK: token_type={creds.token_type}, expiry={creds.expiry_date}")
    except Exception as e:
        print(f"Parse error: {e}")
"""

# Write script to temp file on VM
run(f"cat > /tmp/test_creds.py << 'HEREDOC'\n{script}\nHEREDOC")

# Run it in the container
out, _ = run("cd /root/se-toolkit-lab-8 && docker exec $(docker compose --env-file .env.docker.secret ps -q qwen-code-api) python3 /tmp/test_creds.py 2>&1")
print(out)

client.close()
