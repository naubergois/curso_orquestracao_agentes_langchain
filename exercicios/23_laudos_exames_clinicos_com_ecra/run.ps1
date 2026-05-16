# Exercício 23 — laudos clínicos demo (Streamlit + Postgres + Chroma). Docker por defeito.
#   .\run.ps1
#   .\run.ps1 -Local
#   .\run.ps1 -Fg

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

if (-not $env:STREAMLIT_PORT) { $env:STREAMLIT_PORT = '8511' }
[int]$portNum = $env:STREAMLIT_PORT

. (Join-Path (Split-Path $ScriptDir -Parent) 'lib_docker_exercicios.ps1')

function Invoke-RunLocalEx23 {
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

    Set-Location $ScriptDir
    if (-not $env:POSTGRES_PORT_EX23) { $env:POSTGRES_PORT_EX23 = '5441' }
    $env:DATABASE_URL = "postgresql://curso:curso@127.0.0.1:$($env:POSTGRES_PORT_EX23)/laudos_clinicos"
    $env:CHROMA_PERSIST_DIR = Join-Path $ScriptDir 'chroma_data'
    Write-Host "Local: http://localhost:$portNum  |  DATABASE_URL=$($env:DATABASE_URL)"
    & $streamlitExe run streamlit_app.py --server.port $portNum --server.headless true --browser.gatherUsageStats false
}

if ($Local) {
    Invoke-RunLocalEx23
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
    Write-Warning "Crie $EnvFile com GOOGLE_API_KEY."
}

Stop-OtherExerciseDocker -CurrentExerciseDirectory $ScriptDir
Stop-ProcessListeningOnPort -Port $portNum

Set-Location $ScriptDir
$url = "http://localhost:$portNum"

$composeEnv = @()
if (Test-Path -LiteralPath $EnvFile) {
    $composeEnv += '--env-file', $EnvFile
}

$useDetach = $Detach -or (-not $Fg)
if ($useDetach) {
    if ($ComposeArgs -and $ComposeArgs.Count -gt 0) {
        docker compose @composeEnv -f docker-compose.yml up --build -d @ComposeArgs
    } else {
        docker compose @composeEnv -f docker-compose.yml up --build -d
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "Docker: $url"
    Write-Host 'Parar: docker compose -f docker-compose.yml down'
} else {
    Write-Host "Docker (primeiro plano): $url"
    if ($ComposeArgs -and $ComposeArgs.Count -gt 0) {
        docker compose @composeEnv -f docker-compose.yml up --build @ComposeArgs
    } else {
        docker compose @composeEnv -f docker-compose.yml up --build
    }
}
