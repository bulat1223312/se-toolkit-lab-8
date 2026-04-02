import subprocess
import sys

print('Testing SSH to VM...')

# Test connection
result = subprocess.run(
    ['sshpass', '-p', '23112010A.z', 'ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=30', 
     'root@10.93.25.49', 'cat /root/se-toolkit-lab-8/nanobot/pyproject.toml'],
    capture_output=True, text=True, timeout=60
)

print('=== pyproject.toml ===')
print(result.stdout)
if result.stderr:
    print('STDERR:', result.stderr)

# Check services
result = subprocess.run(
    ['sshpass', '-p', '23112010A.z', 'ssh', '-o', 'StrictHostKeyChecking=no',
     'root@10.93.25.49', 'cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps'],
    capture_output=True, text=True, timeout=60
)

print('=== Services ===')
print(result.stdout)

# Check MCP
result = subprocess.run(
    ['sshpass', '-p', '23112010A.z', 'ssh', '-o', 'StrictHostKeyChecking=no',
     'root@10.93.25.49', 'docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep "MCP server.*connected"'],
    capture_output=True, text=True, timeout=60
)

print('=== MCP ===')
print(result.stdout)

print('DONE')
