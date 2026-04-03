import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30, allow_agent=False, look_for_keys=False)

def run(cmd, timeout=300):
    _, out, err = client.exec_command(cmd, timeout=timeout)
    o = out.read().decode(errors='replace')
    e = err.read().decode(errors='replace')
    if o: print(o[-2000:] if len(o) > 2000 else o)
    if e: print(f"ERR: {e[-300:]}")
    return o, e

P = "/root/se-toolkit-lab-8"

print("=== Building nanobot ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret build nanobot 2>&1 | tail -15", timeout=600)
print("\n=== Building qwen-code-api ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret build qwen-code-api 2>&1 | tail -10", timeout=300)
print("\n=== Building Flutter ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret build client-web-flutter 2>&1 | tail -10", timeout=300)
print("\n=== DONE BUILDING ===")
client.close()
