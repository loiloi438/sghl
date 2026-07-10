# Build APK release SGHL Patient
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..\mobile

Write-Host "Flutter pub get…"
flutter pub get

Write-Host "Build APK release…"
flutter build apk --release

$apk = "build\app\outputs\flutter-apk\app-release.apk"
if (Test-Path $apk) {
    Write-Host "APK genere : $((Resolve-Path $apk).Path)" -ForegroundColor Green
} else {
    Write-Error "APK introuvable apres le build."
}
