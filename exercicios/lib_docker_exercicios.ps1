# Biblioteca partilhada (Windows PowerShell).
# Projecto Compose = nome da pasta do exercicio (ex.: 01_alo_mundo).

$script:_ExerciciosDockerRoot = $PSScriptRoot

function Stop-OtherExerciseDocker {
    param([string]$CurrentExerciseDirectory)

    $currentResolved = (Resolve-Path -LiteralPath $CurrentExerciseDirectory).Path
    Get-ChildItem -LiteralPath $script:_ExerciciosDockerRoot -Directory -ErrorAction SilentlyContinue |
        ForEach-Object {
            $sub = $_.FullName
            if ($sub -eq $currentResolved) { return }
            $yml = Join-Path $sub "docker-compose.yml"
            if (-not (Test-Path -LiteralPath $yml)) { return }
            Write-Host "A parar Docker do exercicio $($_.Name)…"
            Push-Location $sub
            try {
                docker compose down --remove-orphans 2>$null
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
