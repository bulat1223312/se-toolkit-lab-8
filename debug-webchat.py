#!/usr/bin/env python3
"""Debug webchat channel registration."""

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    print(f"\n--- {cmd[:70]} ---")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out)
    if err: print(f"STDERR: {err}")
    return out, err

# Check if webchat channel is registered as entry point
run("docker exec se-toolkit-lab-8-nanobot-1 python -c \"from importlib.metadata import entry_points; eps = entry_points(); print([ep for ep in (eps if hasattr(eps, '__iter__') else eps.select(group='nanobot.channels')) if 'webchat' in str(ep).lower()])\" 2>&1")

# Check nanobot-webchat entry points
run("docker exec se-toolkit-lab-8-nanobot-1 python -c \"from importlib.metadata import entry_points; eps = entry_points(); channels = eps if hasattr(eps, '__iter__') else eps.select(group='nanobot.channels'); print('\\n'.join(str(e) for e in channels))\" 2>&1")

# Check config
run("docker exec se-toolkit-lab-8-nanobot-1 cat /app/nanobot/config.resolved.json")

# Check if webchat package is properly installed
run("docker exec se-toolkit-lab-8-nanobot-1 pip show nanobot-webchat 2>&1")

# Check entry_points.txt in nanobot-webchat
run("docker exec se-toolkit-lab-8-nanobot-1 find /usr/local -name 'nanobot_webchat*.dist-info' -exec cat {}/entry_points.txt \\; 2>&1")

# Check if websockets module is available
run("docker exec se-toolkit-lab-8-nanobot-1 python -c \"import websockets; print(websockets.__version__)\" 2>&1")

# Try to import webchat channel directly
run("docker exec se-toolkit-lab-8-nanobot-1 python -c \"import nanobot_webchat; print('OK')\" 2>&1")

client.close()
