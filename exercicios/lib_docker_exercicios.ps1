# Biblioteca partilhada (Windows PowerShell).
# Projecto Compose = nome da pasta (ex.: 01_alo_mundo_com_ecra, 01_alo_mundo_sem_ecra).

$script:_ExerciciosDockerRoot = $PSScriptRoot

function Stop-OtherExerciseDocker {
    param([string]$CurrentExerciseDirectory)

    $currentResolved = (Resolve-Path -LiteralPath $CurrentExerciseDirectory).Path
    Get-ChildItem -LiteralPath $script:_ExerciciosDockerRoot -Directory -ErrorAction SilentlyContinue |
        ForEach-Object {
            $sub = $_.FullName
            if ($sub -eq $currentResolved) { return }
            $yml = Join-Path $sub "docker-compose.yml"
            $jy = Join-Path $sub "docker-compose.jupyter.yml"
            $has = (Test-Path -LiteralPath $yml) -or (Test-Path -LiteralPath $jy)
            if (-not $has) { return }
            Push-Location $sub
            try {
                if (Test-Path -LiteralPath $yml) {
                    Write-Host "A parar Docker do exercicio $($_.Name) (compose)…"
                    docker compose down --remove-orphans 2>$null
                }
                if (Test-Path -LiteralPath $jy) {
                    Write-Host "A parar Docker Jupyter de $($_.Name)…"
                    docker compose -f docker-compose.jupyter.yml down --remove-orphans 2>$null
                }
            } finally {
                Pop-Location
            }
        }
}

function Stop-ProcessListeningOnPort {
    param([int]$Port)

    try {
        $pids = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty OwningProcess -Unique |
                Where-Object { $_ -and $_ -gt 0 })
        foreach ($procId in $pids) {
            Write-Host "A libertar porta $Port (PID $procId)…"
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    } catch {
        Write-Warning "Nao foi possivel listar a porta $Port (abra o PowerShell como admin ou feche o processo manualmente)."
    }
    Start-Sleep -Milliseconds 500
}
