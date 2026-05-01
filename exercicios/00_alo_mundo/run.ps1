# Exercicio 00
#   .\run.ps1                  # Docker: Jupyter com exercicio_0_sem_ecra.ipynb aberto
#   .\run.ps1 -Once            # Docker: main.py uma vez (contentor minimo)
#   .\run.ps1 -Local           # venv local: main.py
#   .\run.ps1 -Notebook        # igual ao predefinido (explicito)

param(
    [switch]$Local,
    [switch]$Once,
    [Alias('jupyter')]
    [switch]$Notebook
)

$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path
$EnvFile = Join-Path $RepoRoot '.env'

. (Join-Path (Split-Path $ScriptDir -Parent) 'lib_docker_exercicios.ps1')

function Invoke-RunLocalEx00 {
    $venvRoot = Join-Path $RepoRoot '.venv'
    $pythonExe = Join-Path $venvRoot 'Scripts\python.exe'
    $req = Join-Path $ScriptDir 'requirements.txt'

    if (-not (Test-Path -LiteralPath $pythonExe)) {
        $py = Get-Command python -ErrorAction SilentlyContinue
        if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
        if (-not $py) { throw 'Instale Python 3 no PATH.' }
        & $py.Source -m venv $venvRoot
    }
    $pip = Join-Path $venvRoot 'Scripts\pip.exe'
    & $pip install -q -r $req

    Set-Location $ScriptDir
    $env:PYTHONUNBUFFERED = '1'
    & $pythonExe -u main.py
}

if ($Local) {
    Invoke-RunLocalEx00
    exit 0
}

if ($Once) {
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
    Set-Location $ScriptDir
    docker compose run --rm --build app
    exit $LASTEXITCODE
}

# Predefinido e -Notebook: Jupyter no Docker
& (Join-Path $ScriptDir 'run_jupyter.ps1')
exit $LASTEXITCODE
