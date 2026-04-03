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

# Find clamp_max_tokens definition
print("=== Finding clamp_max_tokens definition ===")
out, _ = run("grep -r 'def clamp_max_tokens' /root/se-toolkit-lab-8/qwen-code-api/")
print(out)

# Show the function
if out.strip():
    file_path = out.strip().split(':')[0]
    out, _ = run(f"grep -A 15 'def clamp_max_tokens' {file_path}")
    print(f"\nFunction definition:\n{out}")

# Check recent logs
print("\n=== Recent Qwen Logs ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api --tail 20 2>&1 | grep -v opentelemetry")
print(out)

client.close()
