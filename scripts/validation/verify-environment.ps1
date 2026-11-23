# Menu-It WP-01 Environment Verification Script
$ErrorActionPreference = "Continue"

Write-Host "=========================================================="
Write-Host "       MENU-IT FCD-01 / WP-01 ENVIRONMENT VERIFICATION   "
Write-Host "=========================================================="

$results = @()

function Record-TestResult {
    param(
        [string]$TestId,
        [string]$Name,
        [bool]$Passed,
        [string]$Details
    )
    $status = if ($Passed) { "PASS" } else { "FAIL" }
    $script:results += [PSCustomObject]@{
        TestId  = $TestId
        Name    = $Name
        Status  = $status
        Details = $Details
    }
    $color = if ($Passed) { "Green" } else { "Yellow" }
    Write-Host "[$status] $TestId - ${Name}: $Details" -ForegroundColor $color
}

# ENV-001: Git installation
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if ($gitCmd) {
    $gitVer = (git --version).Trim()
    Record-TestResult "ENV-001" "Git Installation" $true $gitVer
} else {
    Record-TestResult "ENV-001" "Git Installation" $false "Git command not found"
}

# ENV-002: Node.js installation
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCmd) {
    $nodeVer = (node --version).Trim()
    Record-TestResult "ENV-002" "Node.js Installation" $true "Node $nodeVer"
} else {
    Record-TestResult "ENV-002" "Node.js Installation" $false "Node command not found"
}

# ENV-003: Python installation
$pyCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pyCmd) {
    $pyVer = (python --version 2>&1).Trim()
    Record-TestResult "ENV-003" "Python Installation" $true $pyVer
} else {
    Record-TestResult "ENV-003" "Python Installation" $false "Python command not found"
}

# ENV-004: Docker installation
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerCmd) {
    $dockerVer = (docker --version 2>&1).Trim()
    Record-TestResult "ENV-004" "Docker CLI Installation" $true $dockerVer
} else {
    Record-TestResult "ENV-004" "Docker CLI Installation" $false "Docker command not found in PATH"
}

# ENV-005: Docker daemon
if ($dockerCmd) {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Record-TestResult "ENV-005" "Docker Daemon Running" $true "Docker daemon responsive"
    } else {
        Record-TestResult "ENV-005" "Docker Daemon Running" $false "Docker daemon not reachable"
    }
} else {
    Record-TestResult "ENV-005" "Docker Daemon Running" $false "Docker CLI unavailable"
}

# ENV-006: pnpm installation
$pnpmCmd = Get-Command pnpm -ErrorAction SilentlyContinue
if ($pnpmCmd) {
    $pnpmOutput = (pnpm --version 2>$null) | Where-Object { $_ -match '^\d+\.\d+' }
    $pnpmVer = if ($pnpmOutput) { $pnpmOutput.Trim() } else { (pnpm --version 2>&1 | Out-String).Trim() }
    Record-TestResult "ENV-006" "pnpm Installation" $true "pnpm v$pnpmVer"
} else {
    Record-TestResult "ENV-006" "pnpm Installation" $false "pnpm command not found"
}

# ENV-007: uv installation
$uvCmd = Get-Command uv -ErrorAction SilentlyContinue
if ($uvCmd) {
    $uvVer = (uv --version 2>&1).Trim()
    Record-TestResult "ENV-007" "uv Installation" $true $uvVer
} else {
    Record-TestResult "ENV-007" "uv Installation" $false "uv command not found in PATH (pip/venv fallback available)"
}

# ENV-008: Workspace creation
$workspacePath = Get-Location
if (Test-Path $workspacePath) {
    Record-TestResult "ENV-008" "Workspace Location" $true "Project directory exists at $workspacePath"
} else {
    Record-TestResult "ENV-008" "Workspace Location" $false "Workspace path not found"
}

Write-Host "`nSummary:"
$results | Format-Table -AutoSize
