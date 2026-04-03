# Скрипт для получения логов с ВМ
$ip = "10.93.25.49"
$password = "23112010A.z"
$user = "root"

# Создаем временный скрипт для SSH
$sshScript = @"
docker compose -f /root/se-toolkit-lab-8/docker-compose.yml logs --tail=50 nanobot
docker compose -f /root/se-toolkit-lab-8/docker-compose.yml logs --tail=30 caddy
docker compose -f /root/se-toolkit-lab-8/docker-compose.yml logs --tail=20 client-web-flutter
docker compose -f /root/se-toolkit-lab-8/docker-compose.yml ps
"@

# Используем plink если доступен, или ssh с ключами
ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=yes "$user@$ip" $sshScript
