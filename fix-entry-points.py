#!/usr/bin/env python3
"""Fix entry points for nanobot-webchat."""

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

# Check if entry_points.txt exists
run("docker exec se-toolkit-lab-8-nanobot-1 find /usr/local -path '*nanobot_webchat*.dist-info*' -type f 2>&1")

# Check direct_url.json
run("docker exec se-toolkit-lab-8-nanobot-1 cat /usr/local/lib/python3.12/site-packages/nanobot_webchat-1.0.0.dist-info/direct_url.json 2>&1")

# Check if there's a RECORD file
run("docker exec se-toolkit-lab-8-nanobot-1 cat /usr/local/lib/python3.12/site-packages/nanobot_webchat-1.0.0.dist-info/RECORD 2>&1 | head -20")

# The issue is editable install doesn't create entry_points.txt
# Need to reinstall without -e flag or manually create entry_points.txt

# Create entry_points.txt manually
run("""docker exec se-toolkit-lab-8-nanobot-1 bash -c 'cat > /usr/local/lib/python3.12/site-packages/nanobot_webchat-1.0.0.dist-info/entry_points.txt << EOF
[nanobot.channels]
webchat = nanobot_webchat:WebChatChannel
EOF
cat /usr/local/lib/python3.12/site-packages/nanobot_webchat-1.0.0.dist-info/entry_points.txt' 2>&1""")

# Verify it was created
run("docker exec se-toolkit-lab-8-nanobot-1 cat /usr/local/lib/python3.12/site-packages/nanobot_webchat-1.0.0.dist-info/entry_points.txt 2>&1")

# Restart nanobot to pick up the entry point
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot 2>&1")

import time
time.sleep(10)

# Check logs
run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail 30")

client.close()
