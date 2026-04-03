#!/usr/bin/env python3
"""SSH-скрипт для пуша изменений на GitHub с ВМ"""
import paramiko

VM_IP = "10.93.25.49"
VM_USER = "root"
VM_PASSWORD = "23112010A.z"
PROJECT_DIR = "/root/se-toolkit-lab-8"


def ssh_exec(ssh, command, timeout=30):
    print(f"$ {command}")
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    if out:
        print(out)
    if err and "Warning" not in err and "notice" not in err.lower():
        print("STDERR:", err)
    return stdout.channel.recv_exit_status(), out, err


def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"Connecting to {VM_IP}...")
    ssh.connect(VM_IP, username=VM_USER, password=VM_PASSWORD, timeout=15)
    print("Connected!\n")

    # Проверить текущий статус git
    print("=== Git status ===")
    ssh_exec(ssh, f"cd {PROJECT_DIR} && git status")

    # Попробовать пуш с токеном (если настроен)
    print("\n=== Try git push ===")
    ssh_exec(ssh, f"cd {PROJECT_DIR} && git push origin main 2>&1 || echo 'Push failed - check credentials'")

    # Альтернатива: сохранить коммит локально для будущего пуша
    print("\n=== Git log (last 3) ===")
    ssh_exec(ssh, f"cd {PROJECT_DIR} && git log --oneline -3")

    ssh.close()
    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
