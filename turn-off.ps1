$ProjectRoot = $PSScriptRoot

Write-Host "Stopping Local Intelligent LMS..." -ForegroundColor Cyan

function Stop-Port {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($connection in $connections) {
        try {
            Stop-Process -Id $connection.OwningProcess -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped process on port $Port" -ForegroundColor Yellow
        } catch {}
    }
}

Write-Host "Stopping frontend, backend, and worker..." -ForegroundColor Yellow

Stop-Port 3000
Stop-Port 3001
Stop-Port 8000

Get-CimInstance Win32_Process |
    Where-Object {
        $_.CommandLine -match "app\.worker" -or
        $_.CommandLine -match "uvicorn app\.main:app" -or
        $_.CommandLine -match "next dev"
    } |
    ForEach-Object {
        try {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped process $($_.ProcessId)" -ForegroundColor Yellow
        } catch {}
    }

Write-Host "Stopping Ollama..." -ForegroundColor Yellow
Stop-Port 11434

Get-CimInstance Win32_Process |
    Where-Object {
        $_.CommandLine -match "ollama serve" -or
        $_.Name -match "ollama"
    } |
    ForEach-Object {
        try {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped Ollama process $($_.ProcessId)" -ForegroundColor Yellow
        } catch {}
    }

Set-Location $ProjectRoot

Write-Host "Stopping Docker services..." -ForegroundColor Yellow
docker compose down

Write-Host ""
Write-Host "Local Intelligent LMS stopped successfully." -ForegroundColor Green