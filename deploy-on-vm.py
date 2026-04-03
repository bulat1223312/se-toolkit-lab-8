#!/usr/bin/env python3
"""Deploy Task 2 on VM via SSH."""

import paramiko
import time
import sys

VM_HOST = '10.93.25.49'
VM_USER = 'root'
VM_PASSWORD = '23112010A.z'

def run_ssh_command(ssh, command, description=""):
    """Run command on VM and print output."""
    if description:
        print(f"\n{'='*60}")
        print(f"📌 {description}")
        print(f"{'='*60}")
    print(f"🔹 Команда: {command}")
    
    stdin, stdout, stderr = ssh.exec_command(command)
    
    output = stdout.read().decode('utf-8', errors='replace')
    err_output = stderr.read().decode('utf-8', errors='replace')
    
    if output:
        print("📤 STDOUT:")
        print(output)
    if err_output:
        print("📤 STDERR:")
        print(err_output)
    
    exit_status = stdout.channel.recv_exit_status()
    print(f"✅ Exit code: {exit_status}" if exit_status == 0 else f"❌ Exit code: {exit_status}")
    
    return exit_status, output, err_output

def main():
    print("🚀 Task 2 Deployment Script")
    print(f"🎯 VM: {VM_HOST}")
    print(f"👤 User: {VM_USER}")
    print()
    
    # Connect to VM
    print("🔌 Подключение к VM...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(VM_HOST, username=VM_USER, password=VM_PASSWORD, timeout=60)
        print("✅ Подключение успешно!\n")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return 1
    
    try:
        # Step 1: Navigate to project directory
        run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && pwd", "Шаг 1: Переход в директорию проекта")
        
        # Step 2: Pull latest changes from git
        run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && git pull origin main", "Шаг 2: Получение обновлений из репозитория")
        
        # Step 3: Check if .env.docker.secret exists
        exit_code, output, _ = run_ssh_command(ssh, "test -f /root/se-toolkit-lab-8/.env.docker.secret && echo 'EXISTS' || echo 'NOT_EXISTS'", "Шаг 3: Проверка .env.docker.secret")
        
        if "NOT_EXISTS" in output:
            print("\n⚠️ .env.docker.secret не найден. Создаю из примера...")
            run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && cp .env.docker.example .env.docker.secret", "Копирование .env.docker.example в .env.docker.secret")
            
            # Get current values and update secret file
            run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && grep -E '^QWEN_CODE_API_KEY=|^NANOBOT_ACCESS_KEY=|^AUTOCHECKER' .env.docker.secret || echo 'Need to set values'", "Текущие значения в .env.docker.secret")
            
            print("\n⚠️ ВНИМАНИЕ: Необходимо вручную установить значения в .env.docker.secret:")
            print("   - QWEN_CODE_API_KEY")
            print("   - NANOBOT_ACCESS_KEY")
            print("   - AUTOCHECKER_API_LOGIN")
            print("   - AUTOCHECKER_API_PASSWORD")
        else:
            print("✅ .env.docker.secret существует")
        
        # Step 4: Check docker-compose.yml
        run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && grep -A 5 '^  nanobot:' docker-compose.yml | head -10", "Шаг 4: Проверка nanobot сервиса в docker-compose.yml")
        
        # Step 5: Check Caddyfile
        run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && grep -A 3 'handle /ws/chat' caddy/Caddyfile", "Шаг 5: Проверка маршрута /ws/chat в Caddyfile")
        run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && grep -A 4 'handle_path /flutter' caddy/Caddyfile", "Шаг 6: Проверка маршрута /flutter в Caddyfile")
        
        # Step 7: Check submodule
        run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && git submodule status", "Шаг 7: Проверка git submodule")
        
        # Step 8: Stop existing services
        run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret down", "Шаг 8: Остановка существующих сервисов")
        
        # Step 9: Build nanobot service
        run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build nanobot", "Шаг 9: Сборка nanobot сервиса")
        
        # Step 10: Build Flutter client
        run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret build client-web-flutter", "Шаг 10: Сборка Flutter клиента")
        
        # Step 11: Start all services
        run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret up -d", "Шаг 11: Запуск всех сервисов")
        
        # Step 12: Check service status
        run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret ps", "Шаг 12: Проверка статуса сервисов")
        
        # Step 13: Check nanobot logs
        run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot --tail 50", "Шаг 13: Проверка логов nanobot")
        
        # Step 14: Check if webchat channel is enabled
        run_ssh_command(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret logs nanobot 2>&1 | grep -i 'webchat\\|channel\\|MCP server'", "Шаг 14: Проверка webchat канала в логах")
        
        # Step 15: Get VM IP for Flutter URL
        run_ssh_command(ssh, "hostname -I | awk '{print $1}'", "Шаг 15: Получение IP адреса VM")
        
        print("\n" + "="*60)
        print("✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО")
        print("="*60)
        print("\n📌 Следующие шаги:")
        print("1. Откройте http://10.93.25.49:42002/flutter в браузере")
        print("2. Войдите с NANOBOT_ACCESS_KEY (указан в .env.docker.secret)")
        print("3. Протестируйте WebSocket:")
        print('   echo \'{"content":"Hello"}\' | websocat "ws://localhost:42002/ws/chat?access_key=YOUR_KEY"')
        print("\n4. Добавьте скриншоты в REPORT.md")
        
    except Exception as e:
        print(f"\n❌ Ошибка выполнения: {e}")
        return 1
    finally:
        ssh.close()
        print("\n🔌 SSH подключение закрыто")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
