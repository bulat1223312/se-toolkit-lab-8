import subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30, allow_agent=False, look_for_keys=False)

def run(cmd, timeout=120):
    _, out, err = client.exec_command(cmd, timeout=timeout)
    o = out.read().decode(errors='replace')
    e = err.read().decode(errors='replace')
    if o: print(o)
    if e: print(f"ERR: {e[-300:]}")
    return o, e

P = "/root/se-toolkit-lab-8"

# Start all services
print("=== Starting all services ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret up -d 2>&1", timeout=120)

# Wait
print("\nWaiting 45s for services to start...")
time.sleep(45)

# Check status
print("\n=== Service Status ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret ps 2>&1")

# Nanobot logs
print("\n=== Nanobot Startup Logs ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret logs nanobot --tail 30 2>&1 | grep -E 'WebChat|connected|channels|Agent|error|Error|Using config'")

# Qwen health
print("\n=== Qwen Health ===")
run("curl -s http://localhost:42005/health 2>&1")

# Qwen logs
print("\n=== Qwen Logs ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret logs qwen-code-api --tail 10 2>&1 | grep -v opentelemetry")

print("\n=== DONE ===")
client.close()
