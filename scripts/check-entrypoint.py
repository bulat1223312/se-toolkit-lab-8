#!/usr/bin/env python3
"""Check entrypoint.py on VM."""

import paramiko

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

print('=== Full entrypoint.py ===')
stdin, stdout, stderr = client.exec_command('cat /root/se-toolkit-lab-8/nanobot/entrypoint.py')
content = stdout.read().decode()
print(content)

client.close()
