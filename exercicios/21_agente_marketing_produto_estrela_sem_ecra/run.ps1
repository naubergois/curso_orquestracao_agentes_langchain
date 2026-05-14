# Exercício 21 sem ecrã — Jupyter no Docker (predefinido).
$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot
& (Join-Path $ScriptDir 'run_jupyter.ps1')
exit $LASTEXITCODE
