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

# Find all authentication-related code in chat.py
print("=== All auth-related code in chat.py ===")
out, _ = run("grep -n 'auth\\|Auth\\|credential\\|token\\|Authentication failed' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py")
print(out)

# Show the chat_completions function
print("\n=== Full chat_completions function ===")
out, _ = run("sed -n '/async def chat_completions/,/^async def \\|^def \\|^class /p' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py | head -100")
print(out)

client.close()
