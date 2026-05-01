# Exemplo — SystemMessage + HumanMessage no Docker (sem UI).
# Uso: .\run.ps1
#      .\run.ps1 -Local
#      .\run.ps1 -Local "Qual e a capital do Chile?"
#      .\run.ps1 "Qual e a capital do Chile?"

param(
    [switch]$Local,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$AppArgs
)

$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path
$EnvFile = Join-Path $RepoRoot '.env'

function Invoke-RunLocal {
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
    if ($AppArgs -and $AppArgs.Count -gt 0) {
        & $pythonExe -u main.py @AppArgs
    } else {
        & $pythonExe -u main.py
    }
}

if ($Local) {
    Invoke-RunLocal
    exit $LASTEXITCODE
}

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

Set-Location $ScriptDir
if ($AppArgs -and $AppArgs.Count -gt 0) {
    docker compose run --rm --build app @AppArgs
} else {
    docker compose run --rm --build app
}
exit $LASTEXITCODE
