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

# Show the full auth.py to find where "No credentials found" is raised
print("=== Full auth.py ===")
out, _ = run("cat /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/auth.py")
print(out)

# Check main.py for "No credentials found"
print("\n=== main.py relevant parts ===")
out, _ = run("grep -B 5 -A 5 'No credentials found' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/main.py")
print(out)

# Check chat.py for the error path
print("\n=== chat.py relevant parts ===")
out, _ = run("grep -B 3 -A 3 'No credentials\\|RuntimeError' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py | head -30")
print(out)

client.close()
