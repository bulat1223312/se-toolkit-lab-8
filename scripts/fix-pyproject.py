#!/usr/bin/env python3
"""Fix nanobot pyproject.toml to not use workspace for nanobot-ai."""

import paramiko

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

# Fix pyproject.toml - remove workspace dependency for nanobot-ai
pyproject_content = '''[project]
name = "nanobot"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "nanobot-ai>=0.1.0",
    "pydantic-settings>=2.0.0",
]

[tool.uv.sources]
lms-mcp = { workspace = true }

# Task 2B — WebSocket channel packages
nanobot-webchat = { workspace = true }
mcp-webchat = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''

print("=== Writing new pyproject.toml ===")
stdin, stdout, stderr = client.exec_command("echo '" + pyproject_content.replace("'", "'\"'\"'") + "' > /root/se-toolkit-lab-8/nanobot/pyproject.toml")
print(stdout.read().decode())

# Verify
print("=== Verifying pyproject.toml ===")
stdin, stdout, stderr = client.exec_command("cat /root/se-toolkit-lab-8/nanobot/pyproject.toml")
print(stdout.read().decode())

client.close()
print("=== Done ===")
