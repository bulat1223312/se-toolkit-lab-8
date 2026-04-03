# SSH helper для подключения к ВМ с автоматическим вводом пароля
param(
    [string]$Command
)

$ip = "10.93.25.49"
$password = "23112010A.z"
$user = "root"

# Создаем временный VBS скрипт для отправки пароля
$vbsScript = @"
Set WshShell = WScript.CreateObject("WScript.Shell")
WScript.Sleep 2000
WshShell.SendKeys "$password"
WshShell.SendKeys "{ENTER}"
WScript.Sleep 1000
"@

$vbsPath = "$env:TEMP\ssh_sendpass.vbs"
$vbsScript | Out-File -FilePath $vbsPath -Encoding ASCII

# Запускаем VBS скрипт в фоне для отправки пароля
Start-Process "wscript.exe" -ArgumentList "`"$vbsPath`"" -WindowStyle Hidden

# Запускаем SSH
ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password "$user@$ip" $Command

# Очищаем временный файл
Remove-Item $vbsPath -Force -ErrorAction SilentlyContinue
