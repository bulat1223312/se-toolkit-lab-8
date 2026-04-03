import subprocess
import sys
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)

import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode(), stderr.read().decode()

# Check the qwen-code-api credentials loading code
print("=== How qwen-code-api loads credentials ===")
out, _ = run("grep -r 'No credentials found\\|load_credentials\\|creds_file\\|oauth_creds' /root/se-toolkit-lab-8/qwen-code-api/src/ | head -20")
print(out)

# Check the AuthManager class
print("\n=== AuthManager code ===")
out, _ = run("grep -A 30 'class AuthManager\\|def load_credentials' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/auth.py 2>/dev/null | head -50")
print(out)

# Check if there's an auth.py
print("\n=== Auth files in qwen-code-api ===")
out, _ = run("find /root/se-toolkit-lab-8/qwen-code-api/src -name '*.py' | xargs grep -l 'credentials\\|auth' | head -10")
print(out)

# Read the actual creds loading logic
print("\n=== Full auth.py ===")
out, _ = run("cat /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/auth.py 2>/dev/null || echo 'no auth.py'")
print(out[:2000] if out else "No auth.py found")

# Check expiry
print("\n=== Check token expiry ===")
out, _ = run("python3 -c \"import json; creds=json.load(open('/root/.qwen/oauth_creds.json')); expiry=creds['expiry_date']/1000; import datetime; print(f'Expiry: {datetime.datetime.fromtimestamp(expiry)}'); print(f'Now: {datetime.datetime.now()}'); print(f'Valid: {expiry > __import__(\"time\").time()}')\" 2>&1")
print(out)

client.close()
