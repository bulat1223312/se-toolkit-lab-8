#!/usr/bin/env python3
"""Fix LLM connection on VM."""

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

print("Step 1: Copy credentials to container")
run_cmd(ssh, "docker cp /root/.qwen/oauth_creds.json se-toolkit-lab-8-qwen-code-api-1:/root/.qwen/oauth_creds.json")

print("Step 2: Disable auth mode")
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && sed -i 's/^QWEN_CODE_API_AUTH_USE=true/QWEN_CODE_API_AUTH_USE=false/' .env.docker.secret")
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && sed -i 's/^QWEN_CODE_AUTH_USE=true/QWEN_CODE_AUTH_USE=false/' .env.docker.secret")
run_cmd(ssh, "grep AUTH_USE /root/se-toolkit-lab-8/.env.docker.secret")

print("Step 3: Fix chat.py to use direct DashScope when auth is disabled")
run_cmd(ssh, '''
docker exec se-toolkit-lab-8-qwen-code-api-1 cp /app/qwen_code_api/routes/chat.py.bak /app/qwen_code_api/routes/chat.py 2>/dev/null || true
''')

# Create fix script on VM
print("Step 4: Apply fix to chat.py")
run_cmd(ssh, "cat > /tmp/fix_chat.py << 'ENDSCRIPT'\nimport re\nwith open('/app/qwen_code_api/routes/chat.py') as f:\n    c = f.read()\nold = '    access_token = await auth.get_valid_token(client)'\nnew = '    if not settings.qwen_code_auth_use:\\n        access_token = settings.qwen_code_api_key\\n        url = f\"{settings.qwen_api_base}/chat/completions\"\\n    else:\\n        access_token = await auth.get_valid_token(client)'\nc = c.replace(old, new)\nold2 = '    creds = auth.load_credentials()\\n    url = f\"{auth.get_api_endpoint(creds)}/chat/completions\"'\nnew2 = '        creds = auth.load_credentials()\\n        url = f\"{auth.get_api_endpoint(creds)}/chat/completions\"'\nc = c.replace(old2, new2)\nold3 = '    headers = build_headers(access_token, streaming=is_streaming)'\nnew3 = '        headers = build_headers(access_token, streaming=is_streaming)'\nc = c.replace(old3, new3)\nwith open('/app/qwen_code_api/routes/chat.py', 'w') as f:\n    f.write(c)\nprint('Fixed!')\nENDSCRIPT\n")

run_cmd(ssh, "docker cp /tmp/fix_chat.py se-toolkit-lab-8-qwen-code-api-1:/tmp/fix_chat.py")
run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 python3 /tmp/fix_chat.py")

print("Step 5: Restart qwen-code-api")
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart qwen-code-api")

print("Step 6: Wait 12 seconds")
time.sleep(12)

print("Step 7: Check health")
exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42005/health")
print(output if output else err)

print("Step 8: Test chat")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
key = api_key.strip()
print(f"Using API key: {key[:20]}...")
exit_code, output, err = run_cmd(ssh, f"curl -m 15 -s http://localhost:42005/v1/chat/completions -H 'X-API-Key: {key}' -H 'Content-Type: application/json' -d '{{\"model\":\"coder-model\",\"messages\":[{{\"role\":\"user\",\"content\":\"say ok\"}}],\"max_tokens\":5}}'", timeout=30)
print(output if output else err)

print("Step 9: Check qwen-code-api logs")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-qwen-code-api-1 2>&1 | tail -20")
print(output if output else err)

print("Step 10: Restart nanobot")
run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot")
time.sleep(15)

print("Step 11: Check nanobot logs")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -iE 'error|LLM|agent loop|Processing|Response|mcp_lms' | tail -15")
print(output if output else err)

ssh.close()
print("DONE")
