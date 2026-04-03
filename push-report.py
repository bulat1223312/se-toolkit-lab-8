#!/usr/bin/env python3
"""Передать REPORT.md на ВМ через SFTP"""
import paramiko

VM_IP = "10.93.25.49"
VM_USER = "root"
VM_PASSWORD = "23112010A.z"
PROJECT_DIR = "/root/se-toolkit-lab-8"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VM_IP, username=VM_USER, password=VM_PASSWORD, timeout=15)

# Передать файл
sftp = ssh.open_sftp()
sftp.put("c:\\Users\\user\\se-toolkit-lab-8\\REPORT.md", f"{PROJECT_DIR}/REPORT.md")
print("REPORT.md uploaded to VM")

# Коммит на ВМ
stdin, stdout, stderr = ssh.exec_command(f"cd {PROJECT_DIR} && git add REPORT.md && git commit -m 'Task 4C: Add bug fix documentation for items.py' && git log --oneline -1")
print(stdout.read().decode())

sftp.close()
ssh.close()
