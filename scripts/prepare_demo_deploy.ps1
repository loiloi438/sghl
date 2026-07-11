# Verifications avant deploiement demo SGHL
$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot ".."
$frontendDist = Join-Path $root "frontend\dist\index.html"
$apk = Join-Path $root "mobile\build\app\outputs\flutter-apk\app-release.apk"
$envProd = Join-Path $root "deploy\.env.production.example"

Write-Host "=== Preparation deploiement demo SGHL ===" -ForegroundColor Cyan

$ok = $true

if (Test-Path $frontendDist) {
    Write-Host "[OK] Build frontend : frontend/dist/" -ForegroundColor Green
} else {
    Write-Host "[!!] Build frontend manquant - lancez: cd frontend; npm run build" -ForegroundColor Yellow
    $ok = $false
}

if (Test-Path $apk) {
    $size = [math]::Round((Get-Item $apk).Length / 1MB, 1)
    Write-Host ('[OK] APK mobile : {0} ({1} Mo)' -f $apk, $size) -ForegroundColor Green
} else {
    Write-Host "[!!] APK absent - lancez: scripts/build_apk.ps1" -ForegroundColor Yellow
}

if (Test-Path $envProd) {
    Write-Host "[OK] Modele prod : deploy/.env.production.example" -ForegroundColor Green
} else {
    Write-Host "[!!] Modele prod introuvable" -ForegroundColor Yellow
    $ok = $false
}

Write-Host ""
Write-Host "Etapes deploiement (Railway / Render) :" -ForegroundColor Cyan
Write-Host "  1. Copier deploy/.env.production.example vers .env sur le serveur"
Write-Host "  2. Renseigner SECRET_KEY, JWT_SECRET, PDF_SIGNING_KEY (50+ car.)"
Write-Host "  3. DEBUG=False, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, HTTPS"
Write-Host "  4. DB PostgreSQL + docker compose up (ou service manage)"
Write-Host "  5. Premier boot : SGHL_SEED_ADMIN=true + SGHL_ADMIN_PASSWORD (puis remettre false)"
Write-Host "  6. Servir frontend/dist/ via nginx ou CDN statique"
Write-Host ""
Write-Host "Guide detaille : docs/HEBERGEMENT.md et docs/DEPLOIEMENT.md"
Write-Host ""

if ($ok) {
    Write-Host "Artefacts locaux prets pour la demo." -ForegroundColor Green
} else {
    Write-Host "Completez les elements manquants ci-dessus." -ForegroundColor Yellow
    exit 1
}
