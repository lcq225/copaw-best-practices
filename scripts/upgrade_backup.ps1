# CoPaw 升级备份脚本 v1.0
# 用法: .\upgrade_backup.ps1 -Action backup|verify|restore
# 
# 配置说明：请根据实际情况修改下面的路径

param(
    [string]$Action = "backup",
    [string]$BackupPath = "",
    [string]$CopawRoot = "",    # CoPaw 根目录，如 "D:\path\to\your\project"
    [string]$BackupRoot = ""    # 备份目录，如 "D:\Backup"
)

# ====== 路径配置（请修改为你的实际路径）======
if (-not $CopawRoot) {
    # 尝试自动检测：脚本在 .copaw/scripts/ 目录下
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    if ($scriptDir -like "*\.copaw\scripts*") {
        $CopawRoot = Split-Path (Split-Path (Split-Path $scriptDir -Parent) -Parent) -Parent
    } else {
        Write-Host "[ERROR] 请通过 -CopawRoot 参数指定 CoPaw 根目录" -ForegroundColor Red
        Write-Host "示例: .\upgrade_backup.ps1 -Action backup -CopawRoot 'D:\path\to\your\project'" -ForegroundColor Yellow
        exit 1
    }
}

if (-not $BackupRoot) {
    $BackupRoot = "D:\Backup"  # 默认备份目录
}

$copawPath = "$CopawRoot\.copaw"
$secretPath = "$CopawRoot\.copaw.secret"

function Write-Success { Write-Host "[OK] $args" -ForegroundColor Green }
function Write-Fail { Write-Host "[FAIL] $args" -ForegroundColor Red }
function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Cyan }

function Invoke-Backup {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "$backupRoot\copaw_upgrade_$timestamp"
    
    Write-Host ""
    Write-Info "Starting backup..."
    Write-Info "Target: $backupDir"
    Write-Host ""
    
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    New-Item -ItemType Directory -Path "$backupDir\.copaw.secret" -Force | Out-Null
    
    $success = 0
    $failed = 0
    
    # Memory DB
    try {
        Copy-Item "$copawPath\.agent-memory\memory.db" "$backupDir\memory.db" -Force
        Write-Success "Memory database"
        $success++
    } catch {
        Write-Fail "Memory database"
        $failed++
    }
    
    # Config
    try {
        Copy-Item "$copawPath\config.json" "$backupDir\config.json" -Force
        Write-Success "Global config"
        $success++
    } catch {
        Write-Fail "Global config"
        $failed++
    }
    
    # Secrets
    try {
        Copy-Item "$secretPath\*" "$backupDir\.copaw.secret\" -Recurse -Force
        Write-Success "Secrets"
        $success++
    } catch {
        Write-Fail "Secrets"
        $failed++
    }
    
    # Agent files
    try {
        Copy-Item "$copawPath\workspaces\default\AGENTS.md" "$backupDir\AGENTS.md" -Force
        Copy-Item "$copawPath\workspaces\default\SOUL.md" "$backupDir\SOUL.md" -Force
        Copy-Item "$copawPath\workspaces\default\PROFILE.md" "$backupDir\PROFILE.md" -Force
        Copy-Item "$copawPath\workspaces\default\MEMORY.md" "$backupDir\MEMORY.md" -Force
        Copy-Item "$copawPath\workspaces\default\HEARTBEAT.md" "$backupDir\HEARTBEAT.md" -Force
        Write-Success "Agent core files"
        $success++
    } catch {
        Write-Fail "Agent core files"
        $failed++
    }
    
    # Global docs
    try {
        Copy-Item "$copawPath\AGENT_MANAGEMENT.md" "$backupDir\AGENT_MANAGEMENT.md" -Force
        Copy-Item "$copawPath\UPGRADE_PLAYBOOK.md" "$backupDir\UPGRADE_PLAYBOOK.md" -Force -ErrorAction SilentlyContinue
        Write-Success "Global management docs"
        $success++
    } catch {
        Write-Fail "Global management docs"
        $failed++
    }
    
    # Templates
    try {
        Copy-Item "$copawPath\templates" "$backupDir\templates" -Recurse -Force
        Write-Success "Templates"
        $success++
    } catch {
        Write-Fail "Templates"
        $failed++
    }
    
    # Backup info
    @{
        timestamp = $timestamp
        backup_dir = $backupDir
        success = $success
        failed = $failed
    } | ConvertTo-Json | Out-File "$backupDir\backup_info.json" -Encoding UTF8
    
    Write-Host ""
    Write-Host "=========================================="
    Write-Success "Backup completed: $success items"
    if ($failed -gt 0) { Write-Fail "Failed: $failed items" }
    Write-Info "Location: $backupDir"
    Write-Host "=========================================="
}

function Invoke-Verify {
    Write-Host ""
    Write-Info "Verifying CoPaw core files..."
    Write-Host ""
    
    $checks = @(
        @{N="Memory DB"; P="$copawPath\.agent-memory\memory.db"},
        @{N="Config"; P="$copawPath\config.json"},
        @{N="AGENTS.md"; P="$copawPath\workspaces\default\AGENTS.md"},
        @{N="SOUL.md"; P="$copawPath\workspaces\default\SOUL.md"},
        @{N="PROFILE.md"; P="$copawPath\workspaces\default\PROFILE.md"},
        @{N="MEMORY.md"; P="$copawPath\workspaces\default\MEMORY.md"},
        @{N="AGENT_MANAGEMENT.md"; P="$copawPath\AGENT_MANAGEMENT.md"},
        @{N="Templates"; P="$copawPath\templates"},
        @{N="Secrets"; P="$secretPath"}
    )
    
    $ok = 0
    $fail = 0
    
    foreach ($c in $checks) {
        if (Test-Path $c.P) {
            Write-Success $c.N
            $ok++
        } else {
            Write-Fail $c.N
            $fail++
        }
    }
    
    Write-Host ""
    Write-Host "=========================================="
    Write-Success "OK: $ok"
    if ($fail -gt 0) { Write-Fail "Missing: $fail" }
    Write-Host "=========================================="
}

function Invoke-Restore {
    if (-not $BackupPath) {
        Write-Fail "Please specify -BackupPath"
        Write-Info "Available backups:"
        Get-ChildItem "$backupRoot\copaw_upgrade_*" -Directory | 
            Sort-Object Name -Descending | 
            Select-Object -First 5 | 
            ForEach-Object { Write-Host "  $($_.FullName)" }
        return
    }
    
    if (-not (Test-Path $BackupPath)) {
        Write-Fail "Backup path not found: $BackupPath"
        return
    }
    
    Write-Host ""
    Write-Host "[WARNING] This will overwrite current files!" -ForegroundColor Yellow
    Write-Host "Source: $BackupPath"
    Write-Host ""
    Write-Host "Continue? (Y/N): " -NoNewline
    $confirm = Read-Host
    
    if ($confirm -ne "Y" -and $confirm -ne "y") {
        Write-Info "Cancelled"
        return
    }
    
    Write-Info "Restoring..."
    
    try {
        Copy-Item "$BackupPath\memory.db" "$copawPath\.agent-memory\memory.db" -Force
        Write-Success "Memory database"
        
        Copy-Item "$BackupPath\config.json" "$copawPath\config.json" -Force
        Write-Success "Config"
        
        Copy-Item "$BackupPath\AGENTS.md" "$copawPath\workspaces\default\AGENTS.md" -Force
        Copy-Item "$BackupPath\SOUL.md" "$copawPath\workspaces\default\SOUL.md" -Force
        Copy-Item "$BackupPath\PROFILE.md" "$copawPath\workspaces\default\PROFILE.md" -Force
        Copy-Item "$BackupPath\MEMORY.md" "$copawPath\workspaces\default\MEMORY.md" -Force
        Copy-Item "$BackupPath\HEARTBEAT.md" "$copawPath\workspaces\default\HEARTBEAT.md" -Force
        Write-Success "Agent files"
        
        if (Test-Path "$BackupPath\.copaw.secret") {
            Copy-Item "$BackupPath\.copaw.secret\*" $secretPath -Recurse -Force
            Write-Success "Secrets"
        }
        
        Copy-Item "$BackupPath\AGENT_MANAGEMENT.md" "$copawPath\AGENT_MANAGEMENT.md" -Force
        Write-Success "Global management doc"
        
        Write-Host ""
        Write-Host "=========================================="
        Write-Success "Restore completed! Please restart CoPaw."
        Write-Host "=========================================="
    } catch {
        Write-Fail "Restore failed: $_"
    }
}

# Main
Write-Host ""
Write-Host "=========================================="
Write-Host "       CoPaw Upgrade Backup Tool v1.0"
Write-Host "=========================================="

switch ($Action.ToLower()) {
    "backup" { Invoke-Backup }
    "verify" { Invoke-Verify }
    "restore" { Invoke-Restore }
    default {
        Write-Host ""
        Write-Info "Usage:"
        Write-Host "  .\upgrade_backup.ps1 -Action backup"
        Write-Host "  .\upgrade_backup.ps1 -Action verify"
        Write-Host "  .\upgrade_backup.ps1 -Action restore -BackupPath 'D:\Backup\copaw_upgrade_xxx'"
    }
}