# Menu-It — Unified Development Runtime Launcher
$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $root

Write-Host "=========================================================="
Write-Host "         STARTING MENU-IT APPLICATION RUNTIMES            "
Write-Host "=========================================================="
Write-Host "Ports:"
Write-Host "  - Customer Web:    http://localhost:3000"
Write-Host "  - Administration:  http://localhost:3001"
Write-Host "  - Backend API:     http://localhost:8000 (Docs: /api/v1/docs)"
Write-Host "==========================================================`n"

if (-not (Test-Path ".env")) {
    Write-Warning "Root .env file is missing. Generating from .env.example..."
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
    }
}

pnpm dev

if ($LASTEXITCODE -ne 0) {
    throw "One or more Menu-It applications encountered an error."
}
