# SGHL — Application mobile

Flutter 3 · **portail patient** complet et **staff RDV** (médecin, infirmier).

## Fonctionnalités livrées

- Authentification JWT + **MFA par e-mail** (personnel)
- **Inscription patient** + **validation par code e-mail**
- Navigation principale (accueil, RDV, factures, notifications, profil)
- Tableau de bord patient (hospitalisation, doses, constantes)
- Rendez-vous : consultation, création, annulation
- Prescriptions, laboratoire, plans de soins, constantes, doses
- **Factures + paiement en ligne** (MTN / Airtel / Stripe simulé)
- Notifications in-app
- Thème clair / sombre
- Staff : gestion des rendez-vous

## Prérequis

- Flutter SDK 3.10+
- API SGHL sur `http://127.0.0.1:8000`
- Émulateur Android : `10.0.2.2:8000` (voir `lib/core/api_config.dart`)

## Lancer

```powershell
cd mobile
flutter pub get
flutter run
```

## Comptes démo

| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| Patient | `patient` | `Patient@SGHL2026` |
| Médecin | `medecin` | `Medecin@SGHL2026` (+ code MFA e-mail) |

## Inscription patient

1. Écran connexion → **Créer un compte patient**
2. Renseigner un **e-mail réel** → code de validation reçu par mail
3. Valider le compte → se connecter

## Build Android

```powershell
cd mobile
flutter build apk --release
```

APK : `build/app/outputs/flutter-apk/app-release.apk`

Ou depuis la racine du projet : `scripts/build_apk.ps1`

## Configuration API

Modifier `lib/core/api_config.dart` ou les `--dart-define` au build :

```powershell
flutter run --dart-define=SGHL_API_BASE=http://10.0.2.2:8000/api/v1
```
