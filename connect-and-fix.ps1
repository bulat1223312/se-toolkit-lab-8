# PowerShell script to connect to VM and run fix commands
# Uses SSH with password via System.Diagnostics.Process

$vmHost = "10.93.25.49"
$vmUser = "root"
$vmPassword = "23112010A.z"
$projectPath = "/root/se-toolkit-lab-8"

function Invoke-SSHWithPassword {
    param(
        [string]$Command,
        [int]$Timeout = 60
    )
    
    Write-Host "Running: $Command" -ForegroundColor Yellow
    
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "ssh.exe"
    $psi.Arguments = "-o StrictHostKeyChecking=no -o BatchMode=no $($vmUser)@$($vmHost) `"$Command`""
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.RedirectStandardInput = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    $process.Start() | Out-Null
    
    # Wait for password prompt
    Start-Sleep -Milliseconds 1500
    
    # Send password
    $process.StandardInput.WriteLine($vmPassword)
    $process.StandardInput.Flush()
    
    # Wait for completion
    $completed = $process.WaitForExit($Timeout * 1000)
    
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    
    return @{
        Output = $stdout
        Error = $stderr
        ExitCode = $process.ExitCode
        Completed = $completed
    }
}

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Task 2 - VM Connection Test" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Test connection
Write-Host "`nTesting connection..." -ForegroundColor Green
$result = Invoke-SSHWithPassword -Command "hostname && whoami"
if ($result.ExitCode -eq 0) {
    Write-Host "Connected! Host: $($result.Output.Trim())" -ForegroundColor Green
} else {
    Write-Host "Connection failed!" -ForegroundColor Red
    Write-Host "Error: $($result.Error)" -ForegroundColor Red
    exit 1
}

# Run diagnostic commands
$commands = @(
    "cd $projectPath && docker compose ps 2>&1 | head -20",
    "cd $projectPath && docker compose --env-file .env.docker.secret ps 2>&1 | head -20",
    "cd $projectPath && ls -la nanobot/",
    "cd $projectPath && cat nanobot/pyproject.toml",
    "cd $projectPath && docker compose --env-file .env.docker.secret logs nanobot --tail 20 2>&1"
)

foreach ($cmd in $commands) {
    Write-Host "`n--- Command: $($cmd.Substring(0, [Math]::Min(60, $cmd.Length)))... ---" -ForegroundColor Yellow
    $result = Invoke-SSHWithPassword -Command $cmd -Timeout 30
    Write-Host $result.Output
    if ($result.Error) {
        Write-Host "STDERR: $($result.Error)" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 500
}

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Upload FIX-TASK2-VM.sh to VM" -ForegroundColor White
Write-Host "2. Run: ssh root@10.93.25.49 'bash /root/se-toolkit-lab-8/FIX-TASK2-VM.sh'" -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Cyan
