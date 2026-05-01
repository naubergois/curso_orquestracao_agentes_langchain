# Exercicio 04 — Predefinicao: Docker. Venv: -Local (precisa Postgres no host, porta 5433 por defeito).
# Uso: .\run.ps1
#      .\run.ps1 -Local
#      .\run.ps1 -Fg

param(
    [switch]$Local,
    [Alias('foreground')]
    [switch]$Fg,
    [Alias('d')]
    [switch]$Detach,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ComposeArgs
)

$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path
$EnvFile = Join-Path $RepoRoot '.env'

if (-not $env:STREAMLIT_PORT) { $env:STREAMLIT_PORT = '8501' }
[int]$portNum = $env:STREAMLIT_PORT
if (-not $env:POSTGRES_PORT) { $env:POSTGRES_PORT = '5433' }

. (Join-Path (Split-Path $ScriptDir -Parent) 'lib_docker_exercicios.ps1')

function Invoke-RunLocalEx04 {
    Stop-ProcessListeningOnPort -Port $portNum

    $venvRoot = Join-Path $RepoRoot '.venv'
    $pythonExe = Join-Path $venvRoot 'Scripts\python.exe'
    $streamlitExe = Join-Path $venvRoot 'Scripts\streamlit.exe'
    $req = Join-Path $ScriptDir 'requirements.txt'

    if (-not (Test-Path -LiteralPath $pythonExe)) {
        $py = Get-Command python -ErrorAction SilentlyContinue
        if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
        if (-not $py) { throw 'Instale Python 3 no PATH.' }
        & $py.Source -m venv $venvRoot
    }
    if (-not (Test-Path -LiteralPath $streamlitExe)) {
        $pip = Join-Path $venvRoot 'Scripts\pip.exe'
        & $pip install -q -r $req
    }

    if (-not $env:DATABASE_URL) {
        $env:DATABASE_URL = "postgresql://curso:curso@127.0.0.1:$($env:POSTGRES_PORT)/pacientes"
    }

    Set-Location $ScriptDir
    Write-Host "Local (venv): http://localhost:$portNum"
    Write-Host "DATABASE_URL=$($env:DATABASE_URL)"
    & $streamlitExe run streamlit_app.py --server.port $portNum --server.headless true --browser.gatherUsageStats false
}

if ($Local) {
    Invoke-RunLocalEx04
    exit 0
}

$ErrorActionPreference = 'Continue'
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error 'Instale o Docker Desktop.'
    exit 1
}
docker compose version 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error 'docker compose indisponivel.'
    exit 1
}

if (-not (Test-Path -LiteralPath $EnvFile)) {
    Write-Warning "Crie $EnvFile com DEEPSEEK_API_KEY (ex. 4)."
}

Stop-OtherExerciseDocker -CurrentExerciseDirectory $ScriptDir
Stop-ProcessListeningOnPort -Port $portNum

Set-Location $ScriptDir
$url = "http://localhost:$portNum"

$useDetach = $Detach -or (-not $Fg)
if ($useDetach) {
    if ($ComposeArgs -and $ComposeArgs.Count -gt 0) {
        docker compose up --build -d @ComposeArgs
    } else {
        docker compose up --build -d
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "Docker: $url"
    Write-Host 'Parar: docker compose down'
    Write-Host 'Logs:  docker compose logs -f'
} else {
    Write-Host "Docker (primeiro plano): $url"
    if ($ComposeArgs -and $ComposeArgs.Count -gt 0) {
        docker compose up --build @ComposeArgs
    } else {
        docker compose up --build
    }
}
