import subprocess
import sys
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"], capture_output=True)

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.93.25.49', username='root', password='23112010A.z', timeout=30,
               allow_agent=False, look_for_keys=False)

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode(), stderr.read().decode()

# Add debug to main.py lifespan to see what's happening
print("=== Adding debug to main.py ===")

# Read current main.py
out, _ = run("cat /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/main.py")
main_py = out

# Find the lifespan function and add debug
debug_code = '''
    # DEBUG: Print credentials loading info
    log.info(f"DEBUG: auth_use={settings.qwen_code_auth_use}")
    log.info(f"DEBUG: creds_file={settings.creds_file}")
    log.info(f"DEBUG: creds_file exists={settings.creds_file.exists()}")
    if settings.creds_file.exists():
        log.info(f"DEBUG: creds_file size={settings.creds_file.stat().st_size}")
        try:
            content = settings.creds_file.read_text()
            log.info(f"DEBUG: creds_file content[:100]={content[:100]}")
        except Exception as e:
            log.error(f"DEBUG: creds_file read error={e}")
'''

# Insert debug code after "creds = _app.state.auth.load_credentials()"
if 'DEBUG: auth_use=' not in main_py:
    main_py = main_py.replace(
        '    creds = _app.state.auth.load_credentials()',
        debug_code + '\n    creds = _app.state.auth.load_credentials()'
    )

    # Write back
    run(f"""cat > /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/main.py << 'MAINEOF'
{main_py}
MAINEOF""")
    print("Debug code added to main.py")
else:
    print("Debug code already present")

# Rebuild and restart
print("\n=== Rebuilding qwen-code-api ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build qwen-code-api 2>&1 | tail -10", timeout=180)
print(out)

print("\n=== Restarting ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d --force-recreate qwen-code-api 2>&1")
print(out)

import time
time.sleep(15)

# Check startup logs
print("\n=== Startup logs with DEBUG ===")
out, _ = run("cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs qwen-code-api 2>&1 | grep -E 'DEBUG|credentials|No credentials' | head -20")
print(out)

client.close()
