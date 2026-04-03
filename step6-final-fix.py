import subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30, allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    _, out, err = client.exec_command(cmd, timeout=timeout)
    o = out.read().decode(errors='replace')
    if o: print(o[:2000])
    return o, err.read().decode(errors='replace') if err else ''

P = "/root/se-toolkit-lab-8"

# Fix 1: Ensure entry_points.txt exists for webchat channel
print("=== Fix 1: Create entry_points.txt ===")
run("""docker exec se-toolkit-lab-8-nanobot-1 bash -c '
mkdir -p /usr/local/lib/python3.12/site-packages/nanobot_webchat-1.0.0.dist-info/
cat > /usr/local/lib/python3.12/site-packages/nanobot_webchat-1.0.0.dist-info/entry_points.txt << EOF
[nanobot.channels]
webchat = nanobot_webchat:WebChatChannel
EOF
cat /usr/local/lib/python3.12/site-packages/nanobot_webchat-1.0.0.dist-info/entry_points.txt
'""")

# Fix 2: Fix oauth_creds.json path for nonroot user
print("\n=== Fix 2: Fix creds path ===")
# Create directory for nonroot user inside container
run("docker exec se-toolkit-lab-8-qwen-code-api-1 mkdir -p /home/nonroot/.qwen 2>&1")
# Copy creds file
run("docker exec se-toolkit-lab-8-qwen-code-api-1 cp /root/.qwen/oauth_creds.json /home/nonroot/.qwen/oauth_creds.json 2>&1")
# Fix permissions
run("docker exec se-toolkit-lab-8-qwen-code-api-1 chmod 644 /home/nonroot/.qwen/oauth_creds.json 2>&1")
# Verify
run("docker exec se-toolkit-lab-8-qwen-code-api-1 ls -la /home/nonroot/.qwen/ 2>&1")

# Also fix on host - copy creds to a location accessible by container
print("\n=== Fix 3: Ensure host file is readable ===")
run("chmod 644 /root/.qwen/oauth_creds.json")
run("ls -la /root/.qwen/oauth_creds.json")

# Fix 4: Restart nanobot with webchat channel enabled
print("\n=== Fix 4: Restart nanobot ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret restart nanobot 2>&1")
time.sleep(20)

# Check nanobot logs
print("\n=== Nanobot logs after restart ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret logs nanobot 2>&1 | grep -E 'WebChat|channels|connected|Agent|error|Error'")

# Fix 5: Restart qwen-code-api
print("\n=== Fix 5: Restart qwen-code-api ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret restart qwen-code-api 2>&1")
time.sleep(15)

# Check qwen logs
print("\n=== Qwen logs after restart ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret logs qwen-code-api 2>&1 | grep -E 'DEBUG|credentials|No credentials|Default'")

# Test LLM
print("\n=== LLM Test ===")
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
key = out.strip()
run(f"curl -s -m 30 http://localhost:42005/v1/chat/completions -H 'Authorization: Bearer {key}' -H 'Content-Type: application/json' -d '{{\"model\":\"coder-model\",\"messages\":[{{\"role\":\"user\",\"content\":\"say ok\"}}],\"max_tokens\":5}}' 2>&1 | head -5")

print("\n=== DONE ===")
client.close()
