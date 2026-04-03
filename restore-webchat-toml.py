#!/usr/bin/env python3
"""Restore nanobot-webchat pyproject.toml from VM."""

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

stdin, stdout, stderr = client.exec_command("cat /root/se-toolkit-lab-8/nanobot-websocket-channel/nanobot-webchat/pyproject.toml")
content = stdout.read()

with open(r"c:\Users\user\se-toolkit-lab-8\nanobot-websocket-channel\nanobot-webchat\pyproject.toml", 'wb') as f:
    f.write(content)

print("File restored successfully")
print(f"Size: {len(content)} bytes")

# Show content
print("\nContent:")
try:
    print(content.decode('utf-8'))
except:
    print(content.decode('latin-1'))

client.close()
