# Jupyter — ex. 10 sem ecrã (triagem + MongoDB).
$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path
if (-not $env:JUPYTER_PORT) { $env:JUPYTER_PORT = '8888' }
if (-not $env:MONGO_EX10_PORT) { $env:MONGO_EX10_PORT = '27018' }
if (-not $env:OPEN_JUPYTER_BROWSER) { $env:OPEN_JUPYTER_BROWSER = '1' }
if (-not $env:EX10_NOTEBOOK) { $env:EX10_NOTEBOOK = 'exercicio_10_sem_ecra.ipynb' }

. (Join-Path (Split-Path $ScriptDir -Parent) 'lib_docker_exercicios.ps1')

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error 'Instale o Docker Desktop.'
    exit 1
}
docker compose version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error 'docker compose indisponivel.'
    exit 1
}

$EnvFile = Join-Path $RepoRoot '.env'
if (-not (Test-Path -LiteralPath $EnvFile)) {
    Write-Warning "Crie $EnvFile com GOOGLE_API_KEY."
}

$nb = $env:EX10_NOTEBOOK.Replace(' ', '%20')
$labUrl = "http://127.0.0.1:$($env:JUPYTER_PORT)/lab/tree/$nb"

Stop-OtherExerciseDocker -CurrentExerciseDirectory $ScriptDir
Set-Location $ScriptDir

Write-Host ''
Write-Host '  Jupyter Lab — ex. 10 (triagem imagens + MongoDB)'
Write-Host "  URL:  $labUrl"
Write-Host ''

if ($env:OPEN_JUPYTER_BROWSER -eq '1') {
    Start-Job -ScriptBlock {
        param($Url)
        Start-Sleep -Seconds 8
        Start-Process $Url
    } -ArgumentList $labUrl | Out-Null
}

$composeEnv = @()
if (Test-Path -LiteralPath $EnvFile) {
    $composeEnv += '--env-file', $EnvFile
}
docker compose @composeEnv -f docker-compose.jupyter.yml up --build
