#!/usr/bin/env python3
"""Fix and verify on VM."""

import paramiko
import time

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

# Retry connection
for i in range(3):
    try:
        print(f'Attempt {i+1}...')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30, banner_timeout=60)
        print('Connected!')
        
        # Check pyproject.toml
        print('\n=== Checking pyproject.toml ===')
        stdin, stdout, stderr = client.exec_command('cat /root/se-toolkit-lab-8/nanobot/pyproject.toml')
        content = stdout.read().decode()
        print(content)
        
        if 'workspace' in content:
            print('ERROR: workspace found! Fixing...')
            new_content = '''[project]
name = "nanobot"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "nanobot-ai>=0.1.0",
    "pydantic-settings>=2.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''
            stdin, stdout, stderr = client.exec_command(f'echo "{new_content}" > /root/se-toolkit-lab-8/nanobot/pyproject.toml')
            print('Fixed!')
        else:
            print('OK: No workspace')
        
        # Check services
        print('\n=== Services ===')
        stdin, stdout, stderr = client.exec_command('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps')
        print(stdout.read().decode())
        
        # Check MCP
        print('\n=== MCP ===')
        stdin, stdout, stderr = client.exec_command('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep "MCP server.*connected"')
        print(stdout.read().decode())
        
        # Check Flutter
        print('\n=== Flutter ===')
        stdin, stdout, stderr = client.exec_command('curl -s http://localhost:42002/flutter/ | grep -c "Nanobot"')
        print(f'Flutter Nanobot count: {stdout.read().decode().strip()}')
        
        client.close()
        break
    except Exception as e:
        print(f'Error: {e}')
        time.sleep(5)

print('\n=== DONE ===')
