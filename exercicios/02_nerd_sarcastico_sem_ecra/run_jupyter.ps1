# Jupyter no Docker — ex. 2 sem ecrã (so localhost).
# Uso: .\run_jupyter.ps1
#      $env:EX02_NOTEBOOK='outro.ipynb'; .\run_jupyter.ps1

$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path
if (-not $env:JUPYTER_PORT) { $env:JUPYTER_PORT = '8888' }
if (-not $env:OPEN_JUPYTER_BROWSER) { $env:OPEN_JUPYTER_BROWSER = '1' }
if (-not $env:EX02_NOTEBOOK) { $env:EX02_NOTEBOOK = 'exercicio_2_sem_ecra.ipynb' }

. (Join-Path (Split-Path $ScriptDir -Parent) 'lib_docker_exercicios.ps1')

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error 'Instale o Docker Desktop.'
    exit 1
}
docker compose version 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error 'docker compose indisponivel.'
    exit 1
}

$EnvFile = Join-Path $RepoRoot '.env'
if (-not (Test-Path -LiteralPath $EnvFile)) {
    Write-Warning "Crie $EnvFile com GOOGLE_API_KEY."
}

$nb = $env:EX02_NOTEBOOK.Replace(' ', '%20')
$labUrl = "http://127.0.0.1:$($env:JUPYTER_PORT)/lab/tree/$nb"

Stop-OtherExerciseDocker -CurrentExerciseDirectory $ScriptDir
Set-Location $ScriptDir

Write-Host ''
Write-Host '  Jupyter Lab — ex. 2 sem ecra (sem token)'
Write-Host "  URL:  $labUrl"
Write-Host ''

if ($env:OPEN_JUPYTER_BROWSER -eq '1') {
    Start-Job -ScriptBlock {
        param($Url)
        Start-Sleep -Seconds 7
        Start-Process $Url
    } -ArgumentList $labUrl | Out-Null
}

$composeEnv = @()
if (Test-Path -LiteralPath $EnvFile) {
    $composeEnv += '--env-file', $EnvFile
}
docker compose @composeEnv -f docker-compose.jupyter.yml up --build
