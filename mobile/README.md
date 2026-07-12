# SGHL — Application mobile

Flutter 3 · **portail patient** complet et **staff RDV** (admin, médecin, infirmier, secrétaire, comptable en lecture).

## Fonctionnalités livrées

- Authentification JWT + **MFA par e-mail** (personnel)
- **Inscription patient** + **validation par code e-mail**
- Navigation principale (accueil, RDV, messagerie, notifications, profil)
- Tableau de bord patient (hospitalisation, doses, constantes)
- Rendez-vous : demande en attente, validation secrétariat, confirmation et annulation
- Prescriptions, laboratoire, plans de soins, constantes, doses
- **Factures + paiement en ligne** (MTN / Airtel / Stripe simulé)
- Notifications in-app
- Thème clair / sombre
- Staff : gestion des rendez-vous

## Prérequis

- Flutter SDK 3.9+ (stable, ex. 3.35.x avec Dart 3.9)
- API SGHL sur `http://127.0.0.1:8000`
- Émulateur Android : `10.0.2.2:8000` (voir `lib/core/api_config.dart`)

## Lancer

**Important :** l’API Django doit tourner depuis la **racine du projet** (`sghl/`), pas depuis `mobile/`.

Terminal 1 — backend :

```powershell
cd C:\Users\MOUANGA\sghl
.\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

Terminal 2 — application :

```powershell
cd C:\Users\MOUANGA\sghl\mobile
flutter pub get
flutter run
```

### URL de l’API selon la plateforme

| Plateforme | URL utilisée |
|------------|----------------|
| Chrome / Windows desktop | `http://127.0.0.1:8000/api/v1` |
| Émulateur Android | `http://10.0.2.2:8000/api/v1` |
| Téléphone physique (Wi‑Fi) | IP du PC, ex. `--dart-define=API_BASE_URL=http://192.168.1.10:8000/api/v1` |

Si vous voyez `ClientException: Failed to fetch`, le backend n’est pas démarré ou la mauvaise URL est utilisée.

## Connexion depuis un telephone

1. Demarrer le backend : `python manage.py runserver 0.0.0.0:8000`
2. Dans l'app, ouvrir **Serveur SGHL** et saisir l'IP du PC (ex. `http://192.168.1.10:8000/api/v1`)
3. Telephone et PC sur le **meme reseau Wi-Fi**

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
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```
