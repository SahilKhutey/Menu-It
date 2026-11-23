# Menu-It — Developer Setup Automation Script
$ErrorActionPreference = "Stop"

Write-Host "=========================================================="
Write-Host "                MENU-IT DEVELOPER SETUP                   "
Write-Host "=========================================================="

# 1. Prerequisite Checks
Write-Host "`n[1/4] Checking prerequisites..."

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or not in PATH."
}
Write-Host "  - Git: $(git --version)"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw "Node.js is not installed or not in PATH."
}
Write-Host "  - Node: $(node --version)"

if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
    throw "pnpm is not installed. Run: npm install -g pnpm"
}
$pnpmVer = (pnpm --version 2>$null) | Where-Object { $_ -match '^\d+\.\d+' }
Write-Host "  - pnpm: v$($pnpmVer.Trim())"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not installed or not in PATH."
}
Write-Host "  - Python: $(python --version)"

# Docker check (warning if missing or not running)
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Warning "Docker is not detected in PATH. Local container services will require Docker Desktop."
} else {
    Write-Host "  - Docker: $(docker --version)"
}

# 2. Frontend Dependencies
Write-Host "`n[2/4] Installing frontend dependencies..."
if (Test-Path "frontend") {
    Push-Location "frontend"
    try {
        pnpm install --frozen-lockfile
        Write-Host "  Frontend dependencies installed successfully."
    }
    finally {
        Pop-Location
    }
} else {
    Write-Host "  Frontend directory not found, skipping."
}

# 3. Backend Environment & Dependencies
Write-Host "`n[3/4] Initializing Python virtual environment..."
$venvPath = Join-Path $PSScriptRoot "../../backend/.venv"
$venvPython = Join-Path $venvPath "Scripts/python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "  Creating virtual environment at $venvPath..."
    python -m venv $venvPath
}
Write-Host "  Virtual environment ready: $venvPython"

Write-Host "  Syncing Python dependencies..."
$reqFile = Join-Path $PSScriptRoot "../../backend/requirements.txt"
if (Test-Path $reqFile) {
    & $venvPython -m pip install -q -r $reqFile
    Write-Host "  Backend dependencies verified."
}

# 4. Environment Configuration
Write-Host "`n[4/4] Verifying environment configuration..."
$envFile = Join-Path $PSScriptRoot "../../.env"
$envExample = Join-Path $PSScriptRoot "../../.env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host "  Created .env from .env.example. Please review and update local passwords."
    }
} else {
    Write-Host "  .env file exists."
}

Write-Host "`n=========================================================="
Write-Host "       MENU-IT SETUP COMPLETED SUCCESSFULLY!              "
Write-Host "=========================================================="
Write-Host "Next steps:"
Write-Host "  - Start frontend:  cd frontend; pnpm run dev"
Write-Host "  - Run backend checks: powershell -ExecutionPolicy Bypass -File scripts/development/backend-check.ps1"
Write-Host "  - Start DB container: docker compose -f infrastructure/development/docker-compose.yml up -d`n"
