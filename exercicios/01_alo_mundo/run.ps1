# Exercicio 01 — Streamlit local (venv na raiz do repositorio).
# Uso: .\run.ps1
#      $env:STREAMLIT_PORT=8502; .\run.ps1

$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path
. (Join-Path (Split-Path $ScriptDir -Parent) 'lib_docker_exercicios.ps1')

$Port = if ($env:STREAMLIT_PORT) { [int]$env:STREAMLIT_PORT } else { 8501 }
Stop-ProcessListeningOnPort -Port $Port

$venvRoot = Join-Path $RepoRoot '.venv'
$pythonExe = Join-Path $venvRoot 'Scripts\python.exe'
$streamlitExe = Join-Path $venvRoot 'Scripts\streamlit.exe'
$req = Join-Path $ScriptDir 'requirements.txt'

if (-not (Test-Path -LiteralPath $pythonExe)) {
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
    if (-not $py) { throw 'Instale Python 3 e coloque python ou py no PATH.' }
    & $py.Source -m venv $venvRoot
}

if (-not (Test-Path -LiteralPath $streamlitExe)) {
    $pip = Join-Path $venvRoot 'Scripts\pip.exe'
    & $pip install -q -r $req
}

Set-Location $ScriptDir
Write-Host "Streamlit: http://localhost:$Port"
& $streamlitExe run streamlit_app.py --server.port $Port --server.headless true --browser.gatherUsageStats false
