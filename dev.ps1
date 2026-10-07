$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$api = Join-Path $root "apps\api"
$web = Join-Path $root "apps\web"

Write-Host ""
Write-Host "FireSense local development"
Write-Host "---------------------------"
Write-Host ""

# Check whether backend is already running.
$backendRunning = Get-NetTCPConnection `
  -LocalPort 8000 `
  -State Listen `
  -ErrorAction SilentlyContinue

if (-not $backendRunning) {
    Write-Host "Starting FireSense API..."

    Start-Process powershell `
      -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$api'; uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
      )
}
else {
    Write-Host "API already running on port 8000."
}

# Check whether frontend is already running.
$frontendRunning = Get-NetTCPConnection `
  -LocalPort 3000 `
  -State Listen `
  -ErrorAction SilentlyContinue

if (-not $frontendRunning) {
    Write-Host "Starting FireSense web..."

    Start-Process powershell `
      -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$web'; npm run dev"
      )
}
else {
    Write-Host "Web already running on port 3000."
}

Write-Host ""
Write-Host "Waiting for services..."

Start-Sleep -Seconds 4

try {
    $health = Invoke-RestMethod `
      -Uri "http://127.0.0.1:8000/health" `
      -TimeoutSec 5

    Write-Host "API health: $($health.status)"
}
catch {
    Write-Warning "API health check not ready yet."
}

Write-Host ""
Write-Host "Frontend: http://localhost:3000"
Write-Host "Backend:  http://127.0.0.1:8000"
Write-Host "API docs: http://127.0.0.1:8000/docs"
Write-Host ""

Start-Process "http://localhost:3000"
