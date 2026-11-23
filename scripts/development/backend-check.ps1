# Menu-It — Backend Validation & Quality Checks
$ErrorActionPreference = "Stop"

Write-Host "=========================================================="
Write-Host "                MENU-IT BACKEND QUALITY CHECKS            "
Write-Host "=========================================================="

$rootPath = Resolve-Path (Join-Path $PSScriptRoot "../..")
$backendPath = Join-Path $rootPath "backend"
$venvPython = Join-Path $backendPath ".venv/Scripts/python.exe"

$pythonCmd = if (Test-Path $venvPython) { $venvPython } else { "python" }

Push-Location $rootPath
try {
    # 1. Ruff Linting Check
    Write-Host "`n[1/3] Running Ruff linting on backend..."
    ruff check apps/api/ backend/
    Write-Host "  Ruff linting passed."

    # 2. Ruff Formatting Check
    Write-Host "`n[2/3] Checking code formatting with Ruff..."
    ruff format --check apps/api/ backend/
    Write-Host "  Ruff format check passed."

    # 3. Architecture & API Tests
    Write-Host "`n[3/3] Running API runtime test suite..."
    $env:PYTHONPATH = "apps/api/src;backend"
    python -m pytest -p no:langsmith_plugin apps/api/tests/ -v
    Write-Host "  API runtime tests passed."

    Write-Host "`n=========================================================="
    Write-Host "       BACKEND VALIDATION COMPLETED SUCCESSFULLY!         "
    Write-Host "=========================================================="
}
finally {
    Pop-Location
}
