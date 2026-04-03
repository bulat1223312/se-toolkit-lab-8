#!/usr/bin/env python3
"""
Simple SSH wrapper that handles password prompt.
Usage: python ssh-with-pass.py "command to run"
"""
import subprocess
import sys
import time
import threading

VM = "root@10.93.25.49"
PASSWORD = "23112010A.z"

def reader_thread(stream, name, results):
    """Read from stream and store output."""
    output = []
    for line in stream:
        output.append(line)
        print(line, end='', flush=True)
    results[name] = ''.join(output)

def run_ssh(command):
    """Run SSH command with password."""
    proc = subprocess.Popen(
        ["ssh", "-o", "StrictHostKeyChecking=no", VM, command],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    results = {}
    
    # Start reader threads
    stdout_thread = threading.Thread(target=reader_thread, args=(proc.stdout, "stdout", results))
    stderr_thread = threading.Thread(target=reader_thread, args=(proc.stderr, "stderr", results))
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()
    
    # Wait for password prompt
    time.sleep(2)
    
    # Check if process is still running (might be waiting for password)
    if proc.poll() is None:
        try:
            proc.stdin.write(PASSWORD + '\n')
            proc.stdin.flush()
        except BrokenPipeError:
            pass
    
    # Wait for completion
    try:
        proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        print("\n[TIMEOUT]")
    
    stdout_thread.join(timeout=5)
    stderr_thread.join(timeout=5)
    
    return proc.returncode, results.get("stdout", ""), results.get("stderr", "")

if __name__ == "__main__":
    command = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hostname"
    print(f"Running: {command}")
    rc, out, err = run_ssh(command)
    print(f"\n[EXIT CODE: {rc}]")
    if err and rc != 0:
        print(f"STDERR: {err}")
    sys.exit(rc)
