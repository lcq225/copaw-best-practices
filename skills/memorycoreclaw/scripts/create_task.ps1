# Create Windows Scheduled Task - Weekly Memory Check
# Run as Administrator

$TaskName = "CoPaw_Memory_Check"
$TaskDescription = "CoPaw Memory System Weekly Check"

# Check if task exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Task '$TaskName' exists, updating..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Python interpreter path
$PythonPath = "D:\CoPaw\copaw-env\Scripts\python.exe"
$ScriptPath = "D:\CoPaw\.copaw\workspaces\default\active_skills\memorycoreclaw\scripts\check_memory.py"

# Create task action
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath -WorkingDirectory "D:\CoPaw\.copaw\workspaces\default"

# Create trigger - Weekly Monday 9:30
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "09:30"

# Create task settings
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries

# Create principal (run as current user)
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

# Register task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description $TaskDescription

Write-Host ""
Write-Host "Task created successfully!"
Write-Host ""
Write-Host "Task Name: $TaskName"
Write-Host "Schedule: Every Monday 09:30"
Write-Host "Command: python check_memory.py"
Write-Host ""
Write-Host "If missed, task will run at next startup (StartWhenAvailable)"
Write-Host ""
Write-Host "Management commands:"
Write-Host "  View: Get-ScheduledTask -TaskName '$TaskName'"
Write-Host "  Run: Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "  Disable: Disable-ScheduledTask -TaskName '$TaskName'"
Write-Host "  Delete: Unregister-ScheduledTask -TaskName '$TaskName'"