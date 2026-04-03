#!/usr/bin/env python3
"""Fix nanobot Dockerfile to use pip install instead of uv sync."""

import paramiko

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USERNAME, password=PASSWORD)

# Simpler Dockerfile that doesn't use uv sync
dockerfile_content = '''FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./pyproject.toml
RUN uv pip install --system nanobot-ai pydantic-settings
COPY . ./nanobot/
CMD ["python", "/app/nanobot/entrypoint.py"]
'''

print("=== Writing new Dockerfile ===")
stdin, stdout, stderr = client.exec_command("echo '" + dockerfile_content.replace("'", "'\"'\"'") + "' > /root/se-toolkit-lab-8/nanobot/Dockerfile")
print(stdout.read().decode())

# Verify
print("=== Verifying Dockerfile ===")
stdin, stdout, stderr = client.exec_command("cat /root/se-toolkit-lab-8/nanobot/Dockerfile")
print(stdout.read().decode())

client.close()
print("=== Done ===")
