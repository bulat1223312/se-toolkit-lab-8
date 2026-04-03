#!/usr/bin/env python3
"""
COMPLETE TASK 2 FIX - All changes applied on VM directly.
This script copies all fixed files to VM and runs docker build/up there.
"""

import subprocess
import sys

# Install paramiko
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)

import paramiko
import time
import os

VM_HOST = "10.93.25.49"
VM_USER = "root"
VM_PASSWORD = "23112010A.z"
PROJECT = "/root/se-toolkit-lab-8"

def read_file(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VM_HOST, username=VM_USER, password=VM_PASSWORD, timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=300):
    """Run command on VM."""
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out:
        print(out)
    if err and 'warning' not in err.lower():
        print(f"STDERR: {err[:500]}")
    return out, err

def write_file_on_vm(local_path, remote_path):
    """Copy file from local to VM."""
    content = read_file(local_path)
    # Escape single quotes for heredoc
    escaped = content.replace("'", "'\"'\"'")
    cmd = f"cat > {remote_path} << 'HEREDOC_END'\n{content}\nHEREDOC_END"
    out, err = run(f"cat > {remote_path} << 'HEREDOC_END'\n{content}\nHEREDOC_END", timeout=30)
    return True

print("=" * 70)
print("TASK 2 - COMPLETE FIX ON VM")
print("=" * 70)

# ==================== STEP 1: Copy fixed files to VM ====================
print("\n" + "=" * 70)
print("STEP 1: Copying fixed files to VM")
print("=" * 70)

files_to_copy = [
    ("nanobot/Dockerfile", f"{PROJECT}/nanobot/Dockerfile"),
    ("nanobot/pyproject.toml", f"{PROJECT}/nanobot/pyproject.toml"),
    ("nanobot/entrypoint.py", f"{PROJECT}/nanobot/entrypoint.py"),
    ("nanobot/config.json", f"{PROJECT}/nanobot/config.json"),
    ("docker-compose.yml", f"{PROJECT}/docker-compose.yml"),
    ("caddy/Caddyfile", f"{PROJECT}/caddy/Caddyfile"),
    ("pyproject.toml", f"{PROJECT}/pyproject.toml"),
    ("nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml",
     f"{PROJECT}/nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml"),
    ("nanobot-websocket-channel/mcp-webchat/pyproject.toml",
     f"{PROJECT}/nanobot-websocket-channel/mcp-webchat/pyproject.toml"),
    ("nanobot-websocket-channel/nanobot-webchat/pyproject.toml",
     f"{PROJECT}/nanobot-websocket-channel/nanobot-webchat/pyproject.toml"),
    ("qwen-code-api/src/qwen_code_api/routes/chat.py",
     f"{PROJECT}/qwen-code-api/src/qwen_code_api/routes/chat.py"),
]

for local, remote in files_to_copy:
    local_full = f"c:\\Users\\user\\se-toolkit-lab-8\\{local}"
    if os.path.exists(local_full):
        try:
            content = read_file(local_full)
            # Write to VM via heredoc
            cmd = f"cat > {remote} << 'HEREDOC_EOF'\n{content}\nHEREDOC_EOF"
            run(cmd, timeout=30)
            print(f"  ✓ {local} -> {remote}")
        except Exception as e:
            print(f"  ✗ {local}: {e}")
    else:
        print(f"  ? {local} not found locally")

# ==================== STEP 2: Fix .env.docker.secret on VM ====================
print("\n" + "=" * 70)
print("STEP 2: Fixing .env.docker.secret on VM")
print("=" * 70)

# Set QWEN_CODE_API_AUTH_USE=true
run(f"sed -i 's/QWEN_CODE_API_AUTH_USE=false/QWEN_CODE_API_AUTH_USE=true/' {PROJECT}/.env.docker.secret")
run(f"grep QWEN_CODE_API_AUTH_USE {PROJECT}/.env.docker.secret")

# Fix oauth_creds.json permissions
run(f"chmod 644 /root/.qwen/oauth_creds.json")
run(f"ls -la /root/.qwen/oauth_creds.json")

# ==================== STEP 3: Fix submodule on VM ====================
print("\n" + "=" * 70)
print("STEP 3: Fixing submodules on VM")
print("=" * 70)

run(f"cd {PROJECT} && git submodule update --init --recursive 2>&1 | tail -5")
run(f"cd {PROJECT} && git status --short | head -10")

# ==================== STEP 4: Stop all services ====================
print("\n" + "=" * 70)
print("STEP 4: Stopping all services")
print("=" * 70)

run(f"cd {PROJECT} && docker compose --env-file .env.docker.secret down 2>&1 | tail -10")

# ==================== STEP 5: Build and start ====================
print("\n" + "=" * 70)
print("STEP 5: Building services")
print("=" * 70)

# Build nanobot first
print("\n--- Building nanobot ---")
run(f"cd {PROJECT} && docker compose --env-file .env.docker.secret build nanobot 2>&1 | tail -30", timeout=600)

# Build qwen-code-api
print("\n--- Building qwen-code-api ---")
run(f"cd {PROJECT} && docker compose --env-file .env.docker.secret build qwen-code-api 2>&1 | tail -15", timeout=300)

# Build Flutter client
print("\n--- Building Flutter client ---")
run(f"cd {PROJECT} && docker compose --env-file .env.docker.secret build client-web-flutter 2>&1 | tail -10", timeout=300)

# Start all
print("\n--- Starting all services ---")
run(f"cd {PROJECT} && docker compose --env-file .env.docker.secret up -d 2>&1 | tail -20", timeout=120)

# Wait for startup
print("\nWaiting for services to start...")
time.sleep(30)

# ==================== STEP 6: Verify ====================
print("\n" + "=" * 70)
print("STEP 6: Verification")
print("=" * 70)

# Check all services
print("\n--- Service Status ---")
run(f"cd {PROJECT} && docker compose --env-file .env.docker.secret ps 2>&1")

# Check nanobot logs
print("\n--- Nanobot Logs ---")
run(f"cd {PROJECT} && docker compose --env-file .env.docker.secret logs nanobot --tail 30 2>&1 | grep -E 'WebChat|connected|channels|Agent|error|Error' | head -20")

# Check qwen-code-api
print("\n--- Qwen Code API Status ---")
run(f"curl -s http://localhost:42005/health 2>&1")

# Test LLM
print("\n--- LLM Test ---")
api_key = ""
out, _ = run(f"grep QWEN_CODE_API_KEY {PROJECT}/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
api_key = out.strip()
if api_key:
    run(f"""curl -s -m 30 http://localhost:42005/v1/chat/completions \\
      -H 'Authorization: Bearer {api_key}' \\
      -H 'Content-Type: application/json' \\
      -d '{{"model":"coder-model","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' 2>&1 | head -5""")

# Test WebSocket
print("\n--- WebSocket Test ---")
run(f"grep NANOBOT_ACCESS_KEY {PROJECT}/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")

# Check Flutter
print("\n--- Flutter Check ---")
run(f"docker volume inspect se-toolkit-lab-8_client-web-flutter 2>&1 | head -5")

print("\n" + "=" * 70)
print("FIX COMPLETE")
print("=" * 70)

client.close()
