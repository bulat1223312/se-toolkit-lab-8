#!/usr/bin/env python3
"""Simple fix: restore backup and apply changes."""

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

print("Step 1: Stop container")
run_cmd(ssh, "docker stop se-toolkit-lab-8-qwen-code-api-1")

print("Step 2: Create fix script on VM")
fix_script = r'''cat > /tmp/fix.py << 'EOF'
with open('/app/qwen_code_api/routes/chat.py.bak') as f:
    c = f.read()
c = c.replace(
    "    access_token = await auth.get_valid_token(client)",
    "    if settings.qwen_code_auth_use:\n        access_token = await auth.get_valid_token(client)\n    else:\n        access_token = settings.qwen_code_api_key"
)
c = c.replace(
    '    creds = auth.load_credentials()\n    url = f"{auth.get_api_endpoint(creds)}/chat/completions"',
    '    if settings.qwen_code_auth_use:\n        creds = auth.load_credentials()\n        url = f"{auth.get_api_endpoint(creds)}/chat/completions"\n    else:\n        url = f"{settings.qwen_api_base}/chat/completions"'
)
c = c.replace(
    '    headers = build_headers(access_token, streaming=is_streaming)',
    '    if settings.qwen_code_auth_use:\n        headers = build_headers(access_token, streaming=is_streaming)\n    else:\n        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}\n        if is_streaming:\n            headers["Accept"] = "text/event-stream"'
)
with open('/app/qwen_code_api/routes/chat.py', 'w') as f:
    f.write(c)
print("Done")
EOF'''

run_cmd(ssh, fix_script)

print("Step 3: Copy and run fix")
run_cmd(ssh, "docker cp /tmp/fix.py se-toolkit-lab-8-qwen-code-api-1:/tmp/fix.py")
run_cmd(ssh, "docker start se-toolkit-lab-8-qwen-code-api-1")
time.sleep(3)
exit_code, output, err = run_cmd(ssh, "docker exec se-toolkit-lab-8-qwen-code-api-1 python3 /tmp/fix.py")
print(output if output else err)

print("Step 4: Wait")
time.sleep(8)

print("Step 5: Test")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, "curl -s -X POST http://localhost:42005/v1/chat/completions -H 'Content-Type: application/json' -H 'X-API-Key: " + api_key.strip() + "' -d '{\"model\":\"coder-model\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}],\"max_tokens\":50}'")
print(output if output else err)

print("Step 6: Logs")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-qwen-code-api-1 2>&1 | tail -10")
print(output if output else err)

ssh.close()
