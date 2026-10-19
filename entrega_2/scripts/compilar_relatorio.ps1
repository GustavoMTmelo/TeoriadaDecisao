param(
    [switch]$PublicarPdf
)

$ErrorActionPreference = 'Stop'
$raizProjeto = Split-Path -Parent $PSScriptRoot
$compiladorProjeto = Get-Command pdflatex -ErrorAction SilentlyContinue
if (-not $compiladorProjeto) {
    $miktexUsuarioProjeto = Join-Path $env:LOCALAPPDATA 'Programs/MiKTeX/miktex/bin/x64/pdflatex.exe'
    if (Test-Path -LiteralPath $miktexUsuarioProjeto) {
        $compiladorProjeto = Get-Command $miktexUsuarioProjeto
    }
}
if (-not $compiladorProjeto) {
    throw 'pdflatex não encontrado. Instale MiKTeX ou TeX Live e reabra o terminal para atualizar o PATH.'
}
$saidaProjeto = Join-Path $raizProjeto 'build/latex'
New-Item -ItemType Directory -Force -Path $saidaProjeto | Out-Null
Push-Location -LiteralPath $raizProjeto
try {
    $referenciasEstaveisProjeto = $false
    for ($passagemProjeto = 1; $passagemProjeto -le 5; $passagemProjeto++) {
        & $compiladorProjeto.Source '-synctex=1' '-file-line-error' '-interaction=nonstopmode' '-halt-on-error' '-output-directory' $saidaProjeto 'relatorio.tex'
        if ($LASTEXITCODE -ne 0) {
            throw "Falha na passagem $passagemProjeto. Consulte build/latex/relatorio.log."
        }
        $logProjeto = Get-Content -LiteralPath (Join-Path $saidaProjeto 'relatorio.log') -Raw
        $precisaRepetirProjeto = $logProjeto -match 'Rerun to get cross-references right|Label\(s\) may have changed|rerunfilecheck Warning:'
        if ($passagemProjeto -ge 2 -and -not $precisaRepetirProjeto) {
            $referenciasEstaveisProjeto = $true
            break
        }
    }
    if (-not $referenciasEstaveisProjeto) {
        throw 'Referências não estabilizaram após cinco passagens. Revise build/latex/relatorio.log.'
    }
    $pdfProjeto = Join-Path $saidaProjeto 'relatorio.pdf'
    if (-not (Test-Path -LiteralPath $pdfProjeto)) {
        throw 'O compilador terminou sem produzir build/latex/relatorio.pdf.'
    }
    Write-Output "PDF compilado: $pdfProjeto. Revise todas as páginas antes da entrega."
    if ($PublicarPdf) {
        Copy-Item -LiteralPath $pdfProjeto -Destination (Join-Path $raizProjeto 'relatorio.pdf')
        Write-Output 'PDF da raiz atualizado com a versão compilada.'
    }
}
finally {
    Pop-Location
}
