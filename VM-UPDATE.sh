#!/bin/bash
# Run this on VM to update the lab

cd /root/se-toolkit-lab-8

# Pull latest changes from GitHub
git pull origin main

# Fix pyproject.toml if needed (remove workspace dependencies)
cat > nanobot/pyproject.toml << 'EOF'
[project]
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
EOF

# Rebuild nanobot
docker compose --env-file .env.docker.secret build nanobot

# Restart nanobot
docker compose --env-file .env.docker.secret up -d --force-recreate nanobot

# Wait for startup
sleep 30

# Check status
docker logs se-toolkit-lab-8-nanobot-1 --tail 50
docker compose --env-file .env.docker.secret ps

echo "Done! Check if MCP servers are connected:"
docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep "MCP server.*connected"
