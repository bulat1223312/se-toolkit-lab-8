import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30, allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    _, out, err = client.exec_command(cmd, timeout=timeout)
    return out.read().decode(errors='replace'), err.read().decode(errors='replace')

# Fix chat.py on VM - clamp_max_tokens call and indentation
print("=== Fixing chat.py on VM ===")

# Fix 1: clamp_max_tokens call
run('sed -i \'s/max_tokens = clamp_max_tokens(body.get("max_tokens"))/max_tokens = clamp_max_tokens(model, body.get("max_tokens", 8192))/\' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py')

# Fix 2: indentation on line 111
run('sed -i "111s/^            headers/        headers/" /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py')

# Verify
out, _ = run('grep -n "clamp_max_tokens\|headers = build_headers" /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py')
print(out)

# Stop services
print("\n=== Stopping services ===")
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret down 2>&1 | tail -5")

print("\n=== Ready for build ===")
client.close()
