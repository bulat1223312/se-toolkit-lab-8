#!/usr/bin/env python3
"""Script to fix the lab on VM via SSH."""

import paramiko
import time
import sys

HOST = "10.93.25.49"
USERNAME = "root"
PASSWORD = "23112010A.z"

def run_ssh_command(client, command, timeout=60):
    """Run SSH command and return output."""
    print(f"\n>>> {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err_output = stderr.read().decode('utf-8', errors='replace')
    if output:
        print(output[:2000])  # Limit output
    if err_output:
        print(f"ERROR: {err_output[:1000]}")
    return output, err_output

def main():
    # Connect to VM
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USERNAME, password=PASSWORD)
    print("Connected!")
    
    # Navigate to project directory
    run_ssh_command(client, "cd /root/se-toolkit-lab-8 && pwd")
    
    # Pull latest changes
    run_ssh_command(client, "cd /root/se-toolkit-lab-8 && git pull origin main")
    
    # Check qwen-code-api pyproject.toml for ruff version conflict
    print("\n\n=== Checking qwen-code-api pyproject.toml ===")
    output, _ = run_ssh_command(client, "cat /root/se-toolkit-lab-8/qwen-code-api/pyproject.toml")
    
    # Fix ruff version in qwen-code-api/pyproject.toml
    print("\n\n=== Fixing ruff version conflict ===")
    fix_ruff_cmd = '''cd /root/se-toolkit-lab-8 && sed -i 's/ruff==0.15.8/ruff==0.14.14/g' qwen-code-api/pyproject.toml'''
    run_ssh_command(client, fix_ruff_cmd)
    
    # Verify the fix
    run_ssh_command(client, "grep ruff /root/se-toolkit-lab-8/qwen-code-api/pyproject.toml")
    
    # Check if .env.docker.secret exists
    print("\n\n=== Checking .env.docker.secret ===")
    output, _ = run_ssh_command(client, "ls -la /root/se-toolkit-lab-8/.env.docker.secret 2>&1 || echo 'FILE NOT FOUND'")
    print(output)
    
    # Get HOST_UID and HOST_GID
    print("\n\n=== Getting host UID/GID ===")
    run_ssh_command(client, "id -u && id -g")
    
    # Check docker containers status
    print("\n\n=== Checking Docker containers ===")
    run_ssh_command(client, "docker ps -a")
    
    # Stop all containers
    print("\n\n=== Stopping all containers ===")
    run_ssh_command(client, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret down 2>&1 || echo 'No compose file or containers'")
    
    # Build nanobot service first
    print("\n\n=== Building nanobot service ===")
    run_ssh_command(client, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot 2>&1", timeout=300)
    
    # Build client-web-flutter
    print("\n\n=== Building Flutter client ===")
    run_ssh_command(client, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build client-web-flutter 2>&1", timeout=300)
    
    # Start all services
    print("\n\n=== Starting all services ===")
    run_ssh_command(client, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d 2>&1", timeout=120)
    
    # Check status
    print("\n\n=== Checking service status ===")
    run_ssh_command(client, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps")
    
    # Check nanobot logs
    print("\n\n=== Checking nanobot logs ===")
    run_ssh_command(client, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail 50")
    
    # Test WebSocket endpoint
    print("\n\n=== Testing WebSocket endpoint ===")
    run_ssh_command(client, "curl -s http://localhost:42002/flutter | head -20")
    
    client.close()
    print("\n\n=== SSH session closed ===")

if __name__ == "__main__":
    main()
