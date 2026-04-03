#!/usr/bin/env python3
"""Script to fix Task 2 on VM via SSH."""

import subprocess
import sys

VM_HOST = "10.93.25.49"
VM_USER = "root"
VM_PASSWORD = "23112010A.z"

def ssh_exec(command: str) -> tuple[str, int]:
    """Execute command on VM via SSH with password."""
    # Use sshpass if available, otherwise try pssh/plink
    cmd = f'sshpass -p "{VM_PASSWORD}" ssh -o StrictHostKeyChecking=no {VM_USER}@{VM_HOST} "{command}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    return result.stdout.strip(), result.returncode

def ssh_exec_file(command: str) -> tuple[str, int]:
    """Execute command on VM via SSH using psexec-like approach."""
    # Alternative: use pscp/psftp from PuTTY
    cmd = f'plink -ssh {VM_USER}@{VM_HOST} -pw "{VM_PASSWORD}" -batch "{command}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    return result.stdout.strip(), result.returncode

def main():
    print("=== Task 2 Fix Script ===")
    print("Connecting to VM...")
    
    # Test connection
    stdout, rc = ssh_exec("hostname && whoami")
    if rc != 0:
        print(f"SSH connection failed (rc={rc})")
        print("Trying alternative method...")
        stdout, rc = ssh_exec_file("hostname && whoami")
        if rc != 0:
            print(f"All SSH methods failed. Please check connection manually.")
            sys.exit(1)
    
    print(f"Connected to: {stdout}")
    
    # Step 1: Check current state
    print("\n=== Step 1: Checking current state ===")
    stdout, _ = ssh_exec("cd /root/se-toolkit-lab-8 && docker compose ps")
    print(stdout[:500] if stdout else "No output")
    
    # Step 2: Fix nanobot/pyproject.toml
    print("\n=== Step 2: Checking nanobot/pyproject.toml ===")
    stdout, _ = ssh_exec("cat /root/se-toolkit-lab-8/nanobot/pyproject.toml")
    print(stdout)
    
    # Step 3: Check if nanobot-websocket-channel submodule is initialized
    print("\n=== Step 3: Checking submodule ===")
    stdout, _ = ssh_exec("cd /root/se-toolkit-lab-8 && ls -la nanobot-websocket-channel/")
    print(stdout)
    
    # Step 4: Check .env.docker.secret exists
    print("\n=== Step 4: Checking env file ===")
    stdout, _ = ssh_exec("ls -la /root/se-toolkit-lab-8/.env.docker.secret")
    print(stdout)
    
    print("\n=== Done ===")
    print("Review the output above and fix issues manually if needed.")

if __name__ == "__main__":
    main()
