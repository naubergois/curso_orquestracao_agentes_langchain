# Limpa outputs dos .ipynb em exercicios/ (ver update_notebooks.py).
# Uso: .\update_notebooks.ps1
#      .\update_notebooks.ps1 --dry-run
#      .\update_notebooks.ps1 --also-colab

$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot
$py = Join-Path $ScriptDir 'update_notebooks.py'

if (Get-Command python3 -ErrorAction SilentlyContinue) {
    & python3 $py @args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $py @args
} else {
    Write-Error 'Instale Python 3 (python ou python3 no PATH).'
}
