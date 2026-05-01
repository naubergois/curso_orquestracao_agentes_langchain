# Reconstrói as imagens Docker de todos os exercícios em exercicios/
# Uso: .\rebuild_all_docker.ps1
#      .\rebuild_all_docker.ps1 -NoPull
#      .\rebuild_all_docker.ps1 -NoCache
#      .\rebuild_all_docker.ps1 -WithExemplos

param(
    [switch]$NoPull,
    [switch]$NoCache,
    [switch]$WithExemplos
)

$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error 'Docker não encontrado no PATH.'
}
docker compose version 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error 'docker compose indisponível.'
}

$pullArgs = @()
if (-not $NoPull) { $pullArgs += '--pull' }
$noCacheArgs = @()
if ($NoCache) { $noCacheArgs += '--no-cache' }

$stacks = @(
    @{ Dir = '00_alo_mundo'; File = 'docker-compose.yml' },
    @{ Dir = '00_alo_mundo'; File = 'docker-compose.jupyter.yml' },
    @{ Dir = '01_alo_mundo_com_ecra'; File = 'docker-compose.yml' },
    @{ Dir = '01_alo_mundo_sem_ecra'; File = 'docker-compose.jupyter.yml' },
    @{ Dir = '02_nerd_sarcastico_com_ecra'; File = 'docker-compose.yml' },
    @{ Dir = '02_nerd_sarcastico_sem_ecra'; File = 'docker-compose.jupyter.yml' },
    @{ Dir = '03_calculadora'; File = 'docker-compose.yml' },
    @{ Dir = '03_calculadora_sem_ecra'; File = 'docker-compose.jupyter.yml' },
    @{ Dir = '04_fatores_risco_pacientes'; File = 'docker-compose.yml' },
    @{ Dir = '04_fatores_risco_pacientes_sem_ecra'; File = 'docker-compose.jupyter.yml' },
    @{ Dir = '05_prompt_templates_lcel_sem_ecra'; File = 'docker-compose.jupyter.yml' },
    @{ Dir = '06_memoria_langchain_sem_ecra'; File = 'docker-compose.jupyter.yml' },
    @{ Dir = '07_precos_clima_cotacao'; File = 'docker-compose.yml' },
    @{ Dir = '07_precos_clima_cotacao_sem_ecra'; File = 'docker-compose.jupyter.yml' },
    @{ Dir = '08_chains_complexas_sem_ecra'; File = 'docker-compose.jupyter.yml' }
)

foreach ($s in $stacks) {
    $exDir = Join-Path $ScriptDir $s.Dir
    $yml = Join-Path $exDir $s.File
    if (-not (Test-Path -LiteralPath $yml)) {
        Write-Warning "Em falta: $yml"
        continue
    }
    Write-Host ''
    Write-Host "  docker compose build — $($s.Dir)/$($s.File)"
    Write-Host ''
    Push-Location $exDir
    try {
        $dockerArgs = @('compose', '-f', $s.File, 'build') + $noCacheArgs + $pullArgs
        & docker @dockerArgs
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Pop-Location
    }
}

if ($WithExemplos) {
    $exemploDir = Join-Path (Split-Path $ScriptDir -Parent) 'exemplos/01_system_message_docker'
    $yml = Join-Path $exemploDir 'docker-compose.yml'
    if (-not (Test-Path -LiteralPath $yml)) {
        Write-Warning "Em falta: $yml"
    } else {
        Write-Host ''
        Write-Host '  docker compose build — exemplos/01_system_message_docker'
        Write-Host ''
        Push-Location $exemploDir
        try {
            $dockerArgs = @('compose', '-f', 'docker-compose.yml', 'build') + $noCacheArgs + $pullArgs
            & docker @dockerArgs
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        } finally {
            Pop-Location
        }
    }
}

Write-Host ''
Write-Host 'Concluído: imagens dos exercícios reconstruídas.'
