#!/usr/bin/env python3
"""Step 1: Copy all fixed files to VM."""

import subprocess, sys, os
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)
import paramiko

VM = "10.93.25.49"
USR, PWD = "root", "23112010A.z"
P = "/root/se-toolkit-lab-8"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VM, username=USR, password=PWD, timeout=30, allow_agent=False, look_for_keys=False)

def run(cmd, timeout=30):
    _, out, err = client.exec_command(cmd, timeout=timeout)
    return out.read().decode(errors='replace'), err.read().decode(errors='replace')

files = [
    "nanobot/Dockerfile",
    "nanobot/pyproject.toml",
    "nanobot/entrypoint.py",
    "nanobot/config.json",
    "docker-compose.yml",
    "caddy/Caddyfile",
    "pyproject.toml",
    "nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml",
    "nanobot-websocket-channel/mcp-webchat/pyproject.toml",
    "nanobot-websocket-channel/nanobot-webchat/pyproject.toml",
    "qwen-code-api/src/qwen_code_api/routes/chat.py",
]

print("=== Copying files to VM ===")
for f in files:
    local = f"c:\\Users\\user\\se-toolkit-lab-8\\{f}"
    remote = f"{P}/{f}"
    if os.path.exists(local):
        content = open(local, 'r', encoding='utf-8', errors='replace').read()
        cmd = f"cat > {remote} << 'HEREDOC_END'\n{content}\nHEREDOC_END"
        out, err = run(cmd, timeout=30)
        status = "✓" if not err else f"✗ ({err[:50]})"
        print(f"  {status} {f}")
    else:
        print(f"  ? {f} not found")

# Fix .env.docker.secret
print("\n=== Fixing .env.docker.secret ===")
run(f"sed -i 's/QWEN_CODE_API_AUTH_USE=false/QWEN_CODE_API_AUTH_USE=true/' {P}/.env.docker.secret")
out, _ = run(f"grep QWEN_CODE_API_AUTH_USE {P}/.env.docker.secret")
print(f"  Auth use: {out.strip()}")

# Fix permissions
run(f"chmod 644 /root/.qwen/oauth_creds.json")

print("\n=== DONE ===")
client.close()
