#!/usr/bin/env python3
"""Fix nanobot Dockerfile and pyproject.toml on VM."""

import paramiko

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

# Fix Dockerfile - simpler approach without building a package
dockerfile_content = '''FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./pyproject.toml
RUN uv venv && uv sync --no-dev --no-build
COPY . ./nanobot/
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "/app/nanobot/entrypoint.py"]
'''

print("=== Writing new Dockerfile ===")
stdin, stdout, stderr = client.exec_command("echo '" + dockerfile_content.replace("'", "'\"'\"'") + "' > /root/se-toolkit-lab-8/nanobot/Dockerfile")
print(stdout.read().decode())

# Fix pyproject.toml - add nanobot-ai and webchat packages
pyproject_content = '''[project]
name = "nanobot"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "nanobot-ai>=0.1.0",
    "pydantic-settings>=2.0.0",
]

[tool.uv.sources]
nanobot-ai = { workspace = true }
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

# Verify files
print("=== Verifying Dockerfile ===")
stdin, stdout, stderr = client.exec_command("cat /root/se-toolkit-lab-8/nanobot/Dockerfile")
print(stdout.read().decode())

print("=== Verifying pyproject.toml ===")
stdin, stdout, stderr = client.exec_command("cat /root/se-toolkit-lab-8/nanobot/pyproject.toml")
print(stdout.read().decode())

client.close()
print("=== Done ===")
