#!/usr/bin/env python3
"""
SSH helper to run commands on VM with password authentication.
Uses subprocess and sends password to stdin.
"""

import subprocess
import sys
import time

VM_HOST = "10.93.25.49"
VM_USER = "root"
VM_PASSWORD = "23112010A.z"

def run_ssh_command(command: str, timeout: int = 60) -> tuple[str, int]:
    """Run command on VM via SSH with password."""
    # Use ssh with password via stdin
    # Note: This requires ssh to accept password from stdin
    # which typically requires SSH_ASKPASS or similar setup
    
    # Alternative: use pssh/plink if available
    # For now, let's try with ssh and expect-like behavior
    
    proc = subprocess.Popen(
        ["ssh", "-o", "StrictHostKeyChecking=no", f"{VM_USER}@{VM_HOST}", command],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a bit for password prompt
    time.sleep(1)
    
    # Try sending password (may not work with all SSH configs)
    try:
        proc.stdin.write(VM_PASSWORD + "\n")
        proc.stdin.flush()
    except:
        pass
    
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return stdout.strip(), proc.returncode
    except subprocess.TimeoutExpired:
        proc.kill()
        return "Timeout", -1

def run_ssh_command_file(command: str, timeout: int = 60) -> tuple[str, int]:
    """Run command using a file to store password."""
    # Create a temporary script that sets up SSH keys first
    setup_and_run = f"""
    # First time: copy SSH key
    if [ ! -f ~/.ssh/authorized_keys ] || ! grep -q "Windows" ~/.ssh/authorized_keys 2>/dev/null; then
        echo "Setting up SSH key authentication..."
        mkdir -p ~/.ssh
        chmod 700 ~/.ssh
    fi
    
    # Run the actual command
    {command}
    """
    
    return run_ssh_command(setup_and_run, timeout)

def main():
    """Main function to fix Task 2 on VM."""
    print("=== Task 2 VM Fix Script ===")
    print(f"Target: {VM_USER}@{VM_HOST}")
    print()
    
    commands = [
        ("Check connectivity", "hostname && whoami && pwd"),
        ("Check Docker", "docker --version && docker compose version"),
        ("Check project", "cd /root/se-toolkit-lab-8 && ls -la"),
        ("Check containers", "docker compose ps 2>&1 || docker ps -a"),
        ("Check nanobot config", "cd /root/se-toolkit-lab-8 && cat nanobot/pyproject.toml"),
        ("Check error", "cd /root/se-toolkit-lab-8 && cat nanobot/uv.lock 2>/dev/null | head -5 || echo 'no uv.lock'"),
    ]
    
    for name, cmd in commands:
        print(f"\n--- {name} ---")
        stdout, rc = run_ssh_command(cmd)
        print(f"Exit code: {rc}")
        print(stdout[:500] if stdout else "(no output)")
        time.sleep(0.5)
    
    print("\n=== Summary ===")
    print("If you see 'root' as whoami output, SSH is working!")
    print("Manual steps needed:")
    print("1. Copy FIX-TASK2-VM.sh to VM")
    print("2. Run: chmod +x FIX-TASK2-VM.sh && bash FIX-TASK2-VM.sh")

if __name__ == "__main__":
    main()
