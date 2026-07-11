# Build APK release SGHL Patient
param(
    [string]$ApiBaseUrl = ""
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..\mobile

if ([string]::IsNullOrWhiteSpace($ApiBaseUrl)) {
    $ip = (
        Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.InterfaceAlias -notmatch 'Loopback' -and
            $_.IPAddress -notlike '169.254.*'
        } |
        Select-Object -First 1
    ).IPAddress
    if ($ip) {
        $ApiBaseUrl = "http://${ip}:8000/api/v1"
        Write-Host "API detectee sur le reseau local : $ApiBaseUrl" -ForegroundColor Cyan
    } else {
        Write-Host "IP locale introuvable - build sans API_BASE_URL (config manuelle dans l'app)." -ForegroundColor Yellow
    }
}

Write-Host "Flutter pub get..."
flutter pub get

Write-Host "Build APK release..."
if ($ApiBaseUrl) {
    flutter build apk --release --dart-define=API_BASE_URL=$ApiBaseUrl
} else {
    flutter build apk --release
}

$apk = "build\app\outputs\flutter-apk\app-release.apk"
if (Test-Path $apk) {
    Write-Host "APK genere : $((Resolve-Path $apk).Path)" -ForegroundColor Green
    if ($ApiBaseUrl) {
        Write-Host "L'APK pointe vers : $ApiBaseUrl" -ForegroundColor Green
        Write-Host "Lancez le backend : python manage.py runserver 0.0.0.0:8000" -ForegroundColor Cyan
    }
} else {
    Write-Error "APK introuvable apres le build."
}
