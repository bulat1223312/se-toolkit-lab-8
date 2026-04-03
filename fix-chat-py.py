#!/usr/bin/env python3
"""Read and fix chat.py on VM."""

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

# Read the file
stdin, stdout, stderr = client.exec_command('wc -l /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py')
lines_count = int(stdout.read().decode().strip().split()[0])
print(f"File has {lines_count} lines")

# Read around line 111
stdin, stdout, stderr = client.exec_command('sed -n \'100,130p\' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py')
content = stdout.read().decode()
print("\nLines 100-130:")
for i, line in enumerate(content.split('\n'), 100):
    print(f"{i:3}: {repr(line)}")

# Show the problematic area
print("\n--- Context ---")
stdin, stdout, stderr = client.exec_command('sed -n \'108,115p\' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py')
print(stdout.read().decode())

# Fix: The issue is line 111 has extra indentation
# Need to fix the entire file properly
# Let's read the whole file and fix it
stdin, stdout, stderr = client.exec_command('cat /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py')
full_content = stdout.read().decode()

# Find the issue and fix it
# The line "headers = build_headers(access_token, streaming=is_streaming)" has wrong indentation
lines = full_content.split('\n')
for i, line in enumerate(lines):
    if 'headers = build_headers(access_token, streaming=is_streaming)' in line:
        # Check if it has wrong indentation
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        print(f"\nLine {i+1}: indent={indent}, content={repr(line)}")
        # Fix indentation - should be same level as other lines in the if block
        # Based on context, it should be 8 spaces (inside if block)
        if indent > 8:
            lines[i] = '        ' + stripped
            print(f"Fixed to: {repr(lines[i])}")

fixed_content = '\n'.join(lines)

# Write back
fixed_escaped = fixed_content.replace("'", "'\"'\"'")
client.exec_command(f"""cat > /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py << 'ENDOFFILE'
{fixed_content}
ENDOFFILE""")

# Verify
stdin, stdout, stderr = client.exec_command('sed -n \'108,115p\' /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py')
print("\nAfter fix:")
print(stdout.read().decode())

# Rebuild
stdin, stdout, stderr = client.exec_command(
    'cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build qwen-code-api 2>&1 | tail -10',
    timeout=180
)
print("\nRebuild:")
print(stdout.read().decode())

# Restart
stdin, stdout, stderr = client.exec_command(
    'cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d qwen-code-api 2>&1',
    timeout=60
)
print("\nRestart:")
print(stdout.read().decode())

import time
time.sleep(10)

# Check logs
stdin, stdout, stderr = client.exec_command(
    'cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api --tail 30'
)
print("\nLogs:")
print(stdout.read().decode())

# Health check
stdin, stdout, stderr = client.exec_command('curl -s http://localhost:42005/health')
print("\nHealth:")
print(stdout.read().decode())

client.close()
