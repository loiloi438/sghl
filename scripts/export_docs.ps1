# Export des docs markdown en PDF (nécessite Pandoc + moteur PDF)
$docs = @(
    "DAT.md", "MCD.md", "MLD.md", "API.md",
    "MANUEL_STAFF.md", "MANUEL_PATIENT.md",
    "RAPPORT_QA_SECURITE.md", "DEPLOIEMENT.md", "ECARTS_CDC.md"
)
$root = Join-Path $PSScriptRoot "..\docs"
$out = Join-Path $root "pdf"
New-Item -ItemType Directory -Force -Path $out | Out-Null

if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
    Write-Host "Pandoc non installe. Installez-le : winget install JohnMacFarlane.Pandoc" -ForegroundColor Yellow
    Write-Host "Alternative : ouvrir chaque .md dans VS Code > Apercu > Imprimer en PDF"
    exit 0
}

foreach ($f in $docs) {
    $src = Join-Path $root $f
    if (-not (Test-Path $src)) { continue }
    $pdf = Join-Path $out ($f -replace '\.md$', '.pdf')
    pandoc $src -o $pdf --pdf-engine=wkhtmltopdf 2>$null
    if (-not (Test-Path $pdf)) {
        pandoc $src -o $pdf
    }
    if (Test-Path $pdf) {
        Write-Host "OK $pdf"
    }
}
Write-Host "PDF dans $out"
