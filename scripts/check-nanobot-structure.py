#!/usr/bin/env python3
"""Check nanobot structure on VM."""

import paramiko

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

# Check nanobot directory structure
stdin, stdout, stderr = client.exec_command('ls -la /root/se-toolkit-lab-8/nanobot/')
print('=== nanobot/ contents ===')
print(stdout.read().decode())

# Check if there's a nanobot subdirectory
stdin, stdout, stderr = client.exec_command('find /root/se-toolkit-lab-8/nanobot/ -type d -name nanobot 2>/dev/null')
print('=== nanobot subdirs ===')
print(stdout.read().decode())

# Check pyproject.toml
stdin, stdout, stderr = client.exec_command('cat /root/se-toolkit-lab-8/nanobot/pyproject.toml')
print('=== pyproject.toml ===')
print(stdout.read().decode())

client.close()
