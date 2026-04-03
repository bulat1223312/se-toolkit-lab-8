import paramiko
import time

print('Connecting to 10.93.25.49...')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=120, banner_timeout=120, auth_timeout=120)
    print('SUCCESS!')
    
    # Check pyproject.toml
    stdin, stdout, stderr = client.exec_command('cat /root/se-toolkit-lab-8/nanobot/pyproject.toml')
    print('=== pyproject.toml ===')
    print(stdout.read().decode())
    
    # Check services
    stdin, stdout, stderr = client.exec_command('cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps')
    print('=== Services ===')
    print(stdout.read().decode())
    
    # Check MCP
    stdin, stdout, stderr = client.exec_command('docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep "MCP server.*connected"')
    print('=== MCP ===')
    print(stdout.read().decode())
    
    # Check Flutter
    stdin, stdout, stderr = client.exec_command('curl -s http://localhost:42002/flutter/ | grep -c "Nanobot"')
    print('=== Flutter ===')
    print(f'Nanobot count: {stdout.read().decode().strip()}')
    
    client.close()
except Exception as e:
    print(f'FAILED: {e}')

print('DONE')
