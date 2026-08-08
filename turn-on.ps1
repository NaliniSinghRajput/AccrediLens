$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$Backend = Join-Path $ProjectRoot "backend"
$Frontend = Join-Path $ProjectRoot "frontend"

function Stop-Port {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($connection in $connections) {
        try {
            Stop-Process -Id $connection.OwningProcess -Force -ErrorAction SilentlyContinue
        } catch {}
    }
}

Write-Host "Starting AccrediLens..." -ForegroundColor Cyan

Set-Location $ProjectRoot

Write-Host "Cleaning old LMS frontend/backend processes..." -ForegroundColor Yellow
Stop-Port 3000
Stop-Port 3001
Stop-Port 8000
Stop-Port 8001

Get-CimInstance Win32_Process |
    Where-Object {
        $_.CommandLine -match "app\.worker" -or
        $_.CommandLine -match "uvicorn app\.main:app" -or
        $_.CommandLine -match "next dev"
    } |
    ForEach-Object {
        try {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        } catch {}
    }

Write-Host "Starting Docker services..." -ForegroundColor Yellow
docker compose up -d

Write-Host "Starting Ollama..." -ForegroundColor Yellow
$ollamaPort = Get-NetTCPConnection -LocalPort 11434 -State Listen -ErrorAction SilentlyContinue

if (-not $ollamaPort) {
    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        "ollama serve"
    )

    Start-Sleep -Seconds 6
}

try {
    ollama list | Out-Null
    Write-Host "Ollama is ready." -ForegroundColor Green
} catch {
    Write-Host "Ollama did not start correctly. Open Ollama manually and run this script again." -ForegroundColor Red
    exit 1
}

Write-Host "Starting backend API on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$Backend'; .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
)

Start-Sleep -Seconds 4

Write-Host "Starting background worker..." -ForegroundColor Yellow
Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$Backend'; .\.venv\Scripts\python.exe -m app.worker"
)

Start-Sleep -Seconds 2

Write-Host "Starting frontend on http://localhost:3001 ..." -ForegroundColor Yellow
Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$Frontend'; npm.cmd run dev -- --port 3001"
)

Start-Sleep -Seconds 8
Start-Process "http://localhost:3001"

Write-Host ""
Write-Host "AccrediLens started successfully." -ForegroundColor Green
Write-Host "Frontend: http://localhost:3001"
Write-Host "Backend:  http://localhost:8000/health"
Write-Host "Ollama:   http://localhost:11434"