# Exercicio 01 — Docker Compose.
# Uso: .\run_docker.ps1              (primeiro plano)
#      .\run_docker.ps1 -Detach     (segundo plano)
#      $env:STREAMLIT_PORT=8503

param(
    [Alias('d')]
    [switch]$Detach,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ComposeArgs
)

$ErrorActionPreference = 'Continue'
$ScriptDir = $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path

if (-not $env:STREAMLIT_PORT) { $env:STREAMLIT_PORT = '8501' }
[int]$portNum = $env:STREAMLIT_PORT

$EnvFile = Join-Path $RepoRoot '.env'
. (Join-Path (Split-Path $ScriptDir -Parent) 'lib_docker_exercicios.ps1')

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error 'Docker nao encontrado no PATH. Instale o Docker Desktop.'
    exit 1
}
docker compose version 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error 'Comando docker compose indisponivel.'
    exit 1
}

if (-not (Test-Path -LiteralPath $EnvFile)) {
    Write-Warning "Crie $EnvFile com GOOGLE_API_KEY (veja .env.example)."
}

Stop-OtherExerciseDocker -CurrentExerciseDirectory $ScriptDir
Stop-ProcessListeningOnPort -Port $portNum

Set-Location $ScriptDir
$url = "http://localhost:$($env:STREAMLIT_PORT)"

if ($Detach) {
    if ($ComposeArgs -and $ComposeArgs.Count -gt 0) {
        docker compose up --build -d @ComposeArgs
    } else {
        docker compose up --build -d
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "Servico em segundo plano: $url"
    Write-Host "Parar: docker compose down (nesta pasta)"
    Write-Host "Logs:  docker compose logs -f"
} else {
    Write-Host "URL: $url (Ctrl+C para parar)"
    if ($ComposeArgs -and $ComposeArgs.Count -gt 0) {
        docker compose up --build @ComposeArgs
    } else {
        docker compose up --build
    }
}
