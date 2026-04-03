# PowerShell script to copy SSH key to VM and run commands
$vmHost = "10.93.25.49"
$vmUser = "root"
$vmPassword = "23112010A.z"

# Function to run SSH command with password
function Invoke-SSHCommand {
    param([string]$Command)
    
    $process = Start-Process -FilePath "ssh.exe" `
        -ArgumentList "-o StrictHostKeyChecking=no", "${vmUser}@${vmHost}", $Command `
        -RedirectStandardOutput "$env:TEMP\ssh_out.txt" `
        -RedirectStandardError "$env:TEMP\ssh_err.txt" `
        -PassThru -NoNewWindow
    
    # Wait for password prompt
    Start-Sleep -Seconds 2
    
    # This won't work directly - need different approach
    $process.WaitForExit(30000)
    
    Get-Content "$env:TEMP\ssh_out.txt" -ErrorAction SilentlyContinue
}

# Alternative: Use sshpass-like approach with Python
$pythonScript = @"
import subprocess
import sys

# First, copy the public key to VM
# Then run commands without password
"@

Write-Host "PowerShell SSH approach is limited. Let's use a different method..."
Write-Host "Please manually copy this public key to the VM:"
Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub"
