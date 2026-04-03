#!/usr/bin/env python3
"""Final fix for LLM and close the lab."""

import paramiko
import time

VM_HOST = '10.93.25.49'
VM_USER = 'root'
VM_PASSWORD = '23112010A.z'

def run_cmd(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    return exit_code, output, err

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VM_HOST, username=VM_USER, password=VM_PASSWORD, timeout=60)

print("=== FINAL FIX ===")

# 1. Ensure we're in the right directory
print("\n1. Navigate to project...")
run_cmd(ssh, "cd /root/se-toolkit-lab-8")

# 2. Copy fixed chat.py into container
print("2. Create fix script on VM...")
run_cmd(ssh, """cat > /tmp/fix_chat.py << 'PYEOF'
with open('/app/qwen_code_api/routes/chat.py') as f:
    content = f.read()

# Fix 1: access_token
content = content.replace(
    '    access_token = await auth.get_valid_token(client)',
    '    if not settings.qwen_code_auth_use:\\n        access_token = settings.qwen_code_api_key\\n        url = f"{settings.qwen_api_base}/chat/completions"\\n    else:\\n        access_token = await auth.get_valid_token(client)'
)

# Fix 2: creds and url
content = content.replace(
    '    creds = auth.load_credentials()\\n    url = f"{auth.get_api_endpoint(creds)}/chat/completions"',
    '        creds = auth.load_credentials()\\n        url = f"{auth.get_api_endpoint(creds)}/chat/completions"'
)

# Fix 3: headers
content = content.replace(
    '    headers = build_headers(access_token, streaming=is_streaming)',
    '        headers = build_headers(access_token, streaming=is_streaming)'
)

with open('/app/qwen_code_api/routes/chat.py', 'w') as f:
    f.write(content)
print("Fixed!")
PYEOF
""")

print("3. Copy fix into container...")
run_cmd(ssh, "docker cp /tmp/fix_chat.py se-toolkit-lab-8-qwen-code-api-1:/tmp/fix_chat.py")

# 4. Disable auth in .env.docker.secret
print("4. Disable auth...")
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && sed -i 's/^QWEN_CODE_API_AUTH_USE=true/QWEN_CODE_API_AUTH_USE=false/' .env.docker.secret")
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && sed -i 's/^QWEN_CODE_AUTH_USE=true/QWEN_CODE_AUTH_USE=false/' .env.docker.secret")
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && grep AUTH_USE .env.docker.secret")

# 5. Stop container, apply fix, restart
print("5. Stop container...")
run_cmd(ssh, "docker stop se-toolkit-lab-8-qwen-code-api-1")

print("6. Apply fix...")
run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 python3 /tmp/fix_chat.py 2>/dev/null || echo 'Applying fix on next start'")

# Restore backup if exists
run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 test -f /app/qwen_code_api/routes/chat.py.bak && docker exec se-toolkit-lab-8-qwen-code-api-1 cp /app/qwen_code_api/routes/chat.py.bak /app/qwen_code_api/routes/chat.py || echo 'No backup'")

# Apply fix again after restore
run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 python3 /tmp/fix_chat.py 2>/dev/null || echo 'Fix script not available'")

print("7. Start container...")
run_cmd(ssh, "docker start se-toolkit-lab-8-qwen-code-api-1")

# 8. Wait
print("8. Wait 12 seconds...")
time.sleep(12)

# 9. Verify the fix was applied
print("9. Check if fix applied...")
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 grep 'qwen_code_auth_use' /app/qwen_code_api/routes/chat.py | head -5")
print(output if output else err)

# 10. Test health
print("10. Health check...")
exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42005/health")
print(output if output else err)

# 11. Test chat
print("11. Test LLM chat...")
exit_code, api_key, _ = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && grep '^QWEN_CODE_API_KEY=' .env.docker.secret | cut -d= -f2")
key = api_key.strip()
print(f"API Key: {key[:20]}...")
exit_code, output, err = run_cmd(ssh, "curl -m 20 -s http://localhost:42005/v1/chat/completions -H 'X-API-Key: " + key + "' -H 'Content-Type: application/json' -d '{\"model\":\"coder-model\",\"messages\":[{\"role\":\"user\",\"content\":\"say hello\"}],\"max_tokens\":20}'")
print(output if output else err)

# 12. If still failing, check logs
print("12. Qwen-code-api logs...")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-qwen-code-api-1 2>&1 | tail -25")
print(output if output else err)

# 13. Restart nanobot
print("13. Restart nanobot...")
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot")
time.sleep(15)

# 14. Check nanobot logs
print("14. Nanobot logs...")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -iE 'error|LLM|agent loop|Processing|Response' | tail -10")
print(output if output else err)

ssh.close()
print("\n=== DONE ===")
