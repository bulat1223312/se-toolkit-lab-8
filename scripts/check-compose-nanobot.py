#!/usr/bin/env python3
"""Check and fix docker-compose.yml nanobot section."""

import paramiko

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

# Check docker-compose.yml nanobot section
print('=== docker-compose.yml nanobot section ===')
stdin, stdout, stderr = client.exec_command('grep -A 30 "nanobot:" /root/se-toolkit-lab-8/docker-compose.yml')
print(stdout.read().decode())

# Check if additional_contexts is present
print('=== Full nanobot service ===')
stdin, stdout, stderr = client.exec_command('sed -n "/^  nanobot:/,/^  [a-z]/p" /root/se-toolkit-lab-8/docker-compose.yml | head -40')
print(stdout.read().decode())

client.close()
print('\n=== Done ===')
