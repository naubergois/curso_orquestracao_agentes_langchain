# Exercicio 10 com ecra — Docker (Streamlit + MongoDB).
param(
    [Alias('foreground')]
    [switch]$Fg,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ComposeArgs
)

$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path
if (-not $env:STREAMLIT_PORT) { $env:STREAMLIT_PORT = '8501' }
if (-not $env:MONGO_EX10_PORT) { $env:MONGO_EX10_PORT = '27018' }

. (Join-Path (Split-Path $ScriptDir -Parent) 'lib_docker_exercicios.ps1')

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Write-Error 'Docker em falta.'; exit 1 }
if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot '.env'))) {
    Write-Warning "Crie .env em $RepoRoot"
}
Stop-OtherExerciseDocker -CurrentExerciseDirectory $ScriptDir
Set-Location $ScriptDir

if ($Fg) {
    docker compose up --build @ComposeArgs
} else {
    docker compose up --build -d @ComposeArgs
    Write-Host "http://localhost:$($env:STREAMLIT_PORT)"
}
