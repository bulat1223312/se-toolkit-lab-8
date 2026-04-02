import subprocess
import time

print('=== SSH Test to VM ===')

# Test 1: Check pyproject.toml
print('\n1. Checking pyproject.toml...')
result = subprocess.run(
    'echo 23112010A.z | ssh -o StrictHostKeyChecking=no -o BatchMode=yes root@10.93.25.49 "cat /root/se-toolkit-lab-8/nanobot/pyproject.toml"',
    capture_output=True, text=True, timeout=60, shell=True
)
print('STDOUT:', result.stdout[:1000] if result.stdout else 'EMPTY')
if result.returncode != 0:
    print('Return code:', result.returncode)

# Test 2: Check services
print('\n2. Checking services...')
result = subprocess.run(
    'echo 23112010A.z | ssh -o StrictHostKeyChecking=no -o BatchMode=yes root@10.93.25.49 "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps"',
    capture_output=True, text=True, timeout=60, shell=True
)
print('STDOUT:', result.stdout[:1000] if result.stdout else 'EMPTY')

# Test 3: Check MCP logs
print('\n3. Checking MCP logs...')
result = subprocess.run(
    'echo 23112010A.z | ssh -o StrictHostKeyChecking=no -o BatchMode=yes root@10.93.25.49 "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -c MCP"',
    capture_output=True, text=True, timeout=60, shell=True
)
print('MCP count:', result.stdout.strip() if result.stdout else 'EMPTY')

# Test 4: Check Flutter
print('\n4. Checking Flutter...')
result = subprocess.run(
    'echo 23112010A.z | ssh -o StrictHostKeyChecking=no -o BatchMode=yes root@10.93.25.49 "curl -s http://localhost:42002/flutter/ | grep -c Nanobot"',
    capture_output=True, text=True, timeout=60, shell=True
)
print('Flutter Nanobot count:', result.stdout.strip() if result.stdout else 'EMPTY')

print('\n=== DONE ===')
