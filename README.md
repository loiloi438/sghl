# SGHL — Système de gestion hospitalière

ERP hospitalier (Django 5.2 + Ninja, Vue 3 staff, Flutter patient) pour la gestion des patients, rendez-vous, prescriptions, laboratoire, pharmacie, facturation et soins.

## Prérequis

- Python 3.11+
- Node.js 20+ (interface staff)
- Flutter 3.x (optionnel, app patient)
- Docker (optionnel, PostgreSQL)

## Installation rapide

```powershell
cd c:\Users\MOUANGA\sghl
python -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt
copy .env.example .env
.\.venv\Scripts\python.exe manage.py setup_project
```

La commande `setup_project` applique les migrations et charge les comptes de démonstration.

## Lancement en développement

**Backend** (port 8000) :

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

**Frontend staff** (port 5173) :

```powershell
cd frontend
npm install
npm run dev
```

Ouvrir [http://localhost:5173](http://localhost:5173). Le proxy Vite redirige `/api` vers Django.

- **Staff** : tableau de bord après connexion (`admin`, `medecin`, etc.)
- **Patient** : espace dédié `/patient` — compte `patient` / `Patient@SGHL2026`

**Mobile patient** : voir [mobile/README.md](mobile/README.md).

## Comptes de démonstration

| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| Admin | `admin` | `Admin@SGHL2026` |
| Médecin | `medecin` | `Medecin@SGHL2026` |
| Infirmier | `infirmier` | `Infirmier@SGHL2026` |
| Biologiste | `biologiste` | `Biologiste@SGHL2026` |
| Pharmacien | `pharmacien` | `Pharmacien@SGHL2026` |
| Comptable | `comptable` | `Comptable@SGHL2026` |
| Patient (mobile) | `patient` | `Patient@SGHL2026` |

## PostgreSQL (production / CDC)

```powershell
docker compose up -d db
```

Dans `.env` :

```env
DB_ENGINE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sghl
DB_USER=sghl
DB_PASSWORD=sghl
```

Puis :

```powershell
.\.venv\Scripts\python.exe manage.py setup_project
```

Guide détaillé : [docs/DEPLOIEMENT.md](docs/DEPLOIEMENT.md).

## Build production (frontend)

```powershell
cd frontend
npm run build
```

Les fichiers statiques sont dans `frontend/dist/`. Définir `VITE_API_BASE_URL` (voir `frontend/.env.production.example`) si l’API n’est pas servie sous le même domaine.

## Tests

```powershell
.\.venv\Scripts\python.exe manage.py test
```

La CI GitHub Actions exécute les tests backend et le build Vue à chaque push.

## Structure du projet

| Dossier | Rôle |
|---------|------|
| `api/v1/` | Routes Django Ninja |
| `accounts/`, `patients/`, `rendezvous/`, … | Apps métier |
| `frontend/` | Interface web staff (Vue 3) |
| `mobile/` | Application patient (Flutter) |
| `docs/` | Documentation technique (DAT) |

## Documentation (soutenance / CDC)

Index complet : [docs/README.md](docs/README.md)

| Livrable | Fichier |
|----------|---------|
| DAT | [docs/DAT.md](docs/DAT.md) |
| MCD | [docs/MCD.md](docs/MCD.md) |
| MLD | [docs/MLD.md](docs/MLD.md) |
| Dictionnaire API | [docs/API.md](docs/API.md) |
| Manuel staff | [docs/MANUEL_STAFF.md](docs/MANUEL_STAFF.md) |
| Manuel patient | [docs/MANUEL_PATIENT.md](docs/MANUEL_PATIENT.md) |
| Rapport QA / sécurité | [docs/RAPPORT_QA_SECURITE.md](docs/RAPPORT_QA_SECURITE.md) |
| Déploiement | [docs/DEPLOIEMENT.md](docs/DEPLOIEMENT.md) |

- [frontend/README.md](frontend/README.md) — interface staff

## Docker (API + PostgreSQL)

```powershell
docker compose up -d --build
# API : http://127.0.0.1:8000/api/v1/sante/
# Swagger : http://127.0.0.1:8000/api/v1/docs
```

## APK mobile

```powershell
.\scripts\build_apk.ps1
```

## Commandes utiles

| Commande | Description |
|----------|-------------|
| `manage.py setup_project` | Migrations + seeds démo |
| `manage.py setup_project --skip-seed` | Migrations uniquement |
| `manage.py seed_demo` | Recharger les données de démo |
| `manage.py test` | Suite de tests Django |
| `manage.py export_openapi` | Export `docs/openapi.json` |
