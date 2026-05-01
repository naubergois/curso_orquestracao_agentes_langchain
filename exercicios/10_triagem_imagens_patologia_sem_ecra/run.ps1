# Exercício 10 sem ecrã — Jupyter + MongoDB (Docker).
$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot
& (Join-Path $ScriptDir 'run_jupyter.ps1')
exit $LASTEXITCODE
