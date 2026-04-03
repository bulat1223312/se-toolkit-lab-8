import subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30, allow_agent=False, look_for_keys=False)

def run(cmd, timeout=300):
    _, out, err = client.exec_command(cmd, timeout=timeout)
    o = out.read().decode(errors='replace')
    e = err.read().decode(errors='replace')
    if o: print(o)
    if e: print(f"STDERR: {e[:300]}")
    return o, e

P = "/root/se-toolkit-lab-8"

# Build nanobot
print("=== Building nanobot ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret build nanobot 2>&1 | tail -20", timeout=600)

# Build qwen-code-api
print("\n=== Building qwen-code-api ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret build qwen-code-api 2>&1 | tail -10", timeout=300)

# Build Flutter
print("\n=== Building Flutter client ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret build client-web-flutter 2>&1 | tail -10", timeout=300)

# Start all
print("\n=== Starting all services ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret up -d 2>&1 | tail -20", timeout=120)

# Wait
print("\nWaiting 30s for services to start...")
time.sleep(30)

# Check
print("\n=== Service Status ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret ps 2>&1")

print("\n=== Nanobot Logs ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret logs nanobot --tail 20 2>&1 | grep -E 'WebChat|connected|channels|Agent|error|Error'")

print("\n=== Qwen Health ===")
run("curl -s http://localhost:42005/health 2>&1")

print("\n=== DONE ===")
client.close()
