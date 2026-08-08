$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$Backend = Join-Path $ProjectRoot "backend"
$Frontend = Join-Path $ProjectRoot "frontend"
$BackendPython = Join-Path $Backend ".venv\Scripts\python.exe"

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found. See README.md for prerequisites."
    }
}

function Stop-Port {
    param([int]$Port)
    Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
}

function Wait-Url {
    param([string]$Url, [int]$TimeoutSeconds = 90)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) { return }
        } catch {}
        Start-Sleep -Seconds 2
    } while ((Get-Date) -lt $deadline)
    throw "Timed out waiting for $Url. Inspect the service terminal for the exact error."
}

Write-Host "Starting AccrediLens..." -ForegroundColor Cyan
Require-Command docker
Require-Command ollama
Require-Command npm.cmd

if (-not (Test-Path $BackendPython)) {
    throw "Backend virtual environment is missing. Complete First-time setup in README.md."
}
if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
    throw "Frontend dependencies are missing. Run npm.cmd install inside frontend."
}
if (-not (Test-Path (Join-Path $Backend ".env"))) {
    throw "backend/.env is missing. Copy backend/.env.example and set JWT_SECRET_KEY."
}
if (-not (Test-Path (Join-Path $Frontend ".env.local"))) {
    throw "frontend/.env.local is missing. Copy frontend/.env.example."
}

Set-Location $ProjectRoot
Write-Host "Clearing stale AccrediLens development listeners..." -ForegroundColor Yellow
3000, 3001, 8000, 8001 | ForEach-Object { Stop-Port $_ }

Get-CimInstance Win32_Process |
    Where-Object {
        $_.CommandLine -match "app\.worker" -or
        $_.CommandLine -match "uvicorn app\.main:app" -or
        $_.CommandLine -match "next dev"
    } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

Write-Host "Starting PostgreSQL, Redis and Qdrant..." -ForegroundColor Yellow
docker compose config --quiet
docker compose up -d

if (-not (Get-NetTCPConnection -LocalPort 11434 -State Listen -ErrorAction SilentlyContinue)) {
    Write-Host "Starting Ollama..." -ForegroundColor Yellow
    Start-Process powershell.exe -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "ollama serve")
}
Wait-Url "http://localhost:11434/api/tags" 60

Write-Host "Starting backend API..." -ForegroundColor Yellow
Start-Process powershell.exe -ArgumentList @(
    "-NoExit", "-ExecutionPolicy", "Bypass", "-Command",
    "cd '$Backend'; .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
)
Wait-Url "http://127.0.0.1:8000/health" 90

Write-Host "Starting background worker..." -ForegroundColor Yellow
Start-Process powershell.exe -ArgumentList @(
    "-NoExit", "-ExecutionPolicy", "Bypass", "-Command",
    "cd '$Backend'; .\.venv\Scripts\python.exe -m app.worker"
)

Write-Host "Starting frontend..." -ForegroundColor Yellow
Start-Process powershell.exe -ArgumentList @(
    "-NoExit", "-ExecutionPolicy", "Bypass", "-Command",
    "cd '$Frontend'; npm.cmd run dev -- --port 3001"
)
Wait-Url "http://localhost:3001" 120
Start-Process "http://localhost:3001"

Write-Host ""
Write-Host "AccrediLens is ready." -ForegroundColor Green
Write-Host "Frontend: http://localhost:3001"
Write-Host "Backend:  http://127.0.0.1:8000/health"
Write-Host "Qdrant:  http://localhost:6333"
Write-Host "Ollama:   http://localhost:11434"
