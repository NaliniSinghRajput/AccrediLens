$ErrorActionPreference = "Continue"
$ProjectRoot = $PSScriptRoot

function Stop-Port {
    param([int]$Port)
    Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object {
            Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped listener on port $Port (PID $_)." -ForegroundColor Yellow
        }
}

Write-Host "Stopping AccrediLens..." -ForegroundColor Cyan

3000, 3001, 8000, 8001 | ForEach-Object { Stop-Port $_ }

Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
        $_.CommandLine -match "app\.worker" -or
        $_.CommandLine -match "uvicorn app\.main:app" -or
        $_.CommandLine -match "next dev"
    } |
    ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        Write-Host "Stopped AccrediLens process $($_.ProcessId)." -ForegroundColor Yellow
    }

Set-Location $ProjectRoot
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker compose down
} else {
    Write-Warning "Docker was not found; application processes were stopped, but containers could not be stopped."
}

Write-Host ""
Write-Host "AccrediLens stopped. Ollama was left running because it may be shared by other local applications." -ForegroundColor Green
