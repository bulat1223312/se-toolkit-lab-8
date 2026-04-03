import subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30, allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    _, out, err = client.exec_command(cmd, timeout=timeout)
    o = out.read().decode(errors='replace')
    if o: print(o)
    return o, err.read().decode(errors='replace') if err else ''

P = "/root/se-toolkit-lab-8"

# Full nanobot logs
print("=== Full Nanobot Logs ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret logs nanobot 2>&1 | grep -v 'Requirement already\\|Building\\|Installing\\|Successfully\\|Building wheels\\|WARNING.*pip'")

# Full qwen logs
print("\n=== Qwen Logs (no opentelemetry) ===")
run(f"cd {P} && docker compose --env-file .env.docker.secret logs qwen-code-api 2>&1 | grep -v opentelemetry")

# Test LLM
print("\n=== LLM Test ===")
out, _ = run("grep QWEN_CODE_API_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
key = out.strip()
run(f"""curl -s -m 30 http://localhost:42005/v1/chat/completions -H 'Authorization: Bearer {key}' -H 'Content-Type: application/json' -d '{{"model":"coder-model","messages":[{{"role":"user","content":"say ok"}}],"max_tokens":5}}' 2>&1""")

# Test WebSocket
print("\n=== WebSocket Test ===")
out, _ = run("grep NANOBOT_ACCESS_KEY /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2 | tr -d '[:space:]'")
wskey = out.strip()
run(f"""cd {P} && timeout 15 python3 -c "
import asyncio, json, websockets
async def t():
    uri = f'ws://localhost:42002/ws/chat?access_key={wskey}'
    async with websockets.connect(uri, close_timeout=5) as ws:
        await ws.send(json.dumps({{'content': 'Hello'}}))
        r = await asyncio.wait_for(ws.recv(), timeout=10)
        print(f'WS: {{r[:200]}}')
asyncio.run(t())
" 2>&1 || echo 'WS test done'""")

print("\n=== DONE ===")
client.close()
