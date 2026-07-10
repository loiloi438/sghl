# Guide de déploiement — SGHL

PostgreSQL, Docker et préparation hébergement (livrable CDC).

---

## 1. PostgreSQL en local (recommandé soutenance)

### Étape A — Démarrer PostgreSQL

```powershell
cd c:\Users\MOUANGA\sghl
docker compose up -d db
docker compose ps
```

Attendre `healthy` sur le service `db`.

### Étape B — Configurer `.env`

```env
DEBUG=True
DB_ENGINE=postgresql
DB_NAME=sghl
DB_USER=sghl
DB_PASSWORD=sghl
DB_HOST=localhost
DB_PORT=5432
```

### Étape C — Migrations et données démo

```powershell
.\.venv\Scripts\python.exe manage.py setup_project
```

### Étape D — Vérifier

```powershell
.\.venv\Scripts\python.exe manage.py dbshell
# \dt
# \q
```

```powershell
.\.venv\Scripts\python.exe manage.py runserver
curl http://127.0.0.1:8000/api/v1/sante/
```

---

## 2. Stack Docker complète (API + PostgreSQL)

```powershell
docker compose up -d --build
```

Services :

| Service | Port | Rôle |
|---------|------|------|
| `db` | 5432 | PostgreSQL 16 |
| `api` | 8000 | Django + Gunicorn |

Variables dans `docker-compose.yml` (section `api`). Au premier démarrage, les migrations et `seed_demo` s’exécutent via la commande du conteneur.

**Arrêt :**

```powershell
docker compose down
```

---

## 3. Frontend staff en production

```powershell
cd frontend
npm ci
npm run build
```

Servir `frontend/dist/` :

- via **nginx** (fichier `deploy/nginx.conf` exemple),
- ou intégré au reverse proxy avec `proxy_pass` vers l’API pour `/api`.

Variable optionnelle : `VITE_API_BASE_URL=https://votre-domaine.com/api/v1`

---

## 4. Application mobile (APK)

```powershell
cd c:\Users\MOUANGA\sghl\mobile
flutter pub get
flutter build apk --release
```

**Sortie :** `mobile/build/app/outputs/flutter-apk/app-release.apk`

Adapter `api_config.dart` avec l’URL publique de l’API (pas `localhost` sur téléphone réel).

Script PowerShell : `scripts/build_apk.ps1`

---

## 5. Hébergement suggéré (lien démo)

Options gratuites / étudiant :

| Plateforme | Backend | Base | Frontend |
|------------|---------|------|----------|
| **Railway** | Container Django | PostgreSQL addon | Static site |
| **Render** | Web service | PostgreSQL | Static |
| **VPS** (OVH, etc.) | Docker compose | PostgreSQL local | nginx |

**Checklist mise en ligne :**

- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` et `CORS_ALLOWED_ORIGINS` renseignés
- [ ] Secrets via variables d’environnement (pas dans le repo)
- [ ] HTTPS activé
- [ ] `python manage.py collectstatic` si admin Django utilisé
- [ ] Lien démo noté dans le README racine

---

## 6. Production — variables minimales

```env
DEBUG=False
SECRET_KEY=<générer-50-caractères>
JWT_SECRET=<autre-secret>
ALLOWED_HOSTS=api.votredomaine.com
CORS_ALLOWED_ORIGINS=https://staff.votredomaine.com
DB_ENGINE=postgresql
DB_HOST=db
DB_NAME=sghl
DB_USER=sghl
DB_PASSWORD=<mot-de-passe-fort>
```

### E-mails rendez-vous

En développement, les messages partent vers la **console** Django (`EMAIL_BACKEND=console`). En production, configurer un relais SMTP :

```env
EMAIL_NOTIFICATIONS_ENABLED=True
OTP_MODE=production
DEFAULT_FROM_EMAIL=noreply@votredomaine.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.votredomaine.com
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
EMAIL_USE_TLS=True
```

Pour les environnements de développement ou de test, `OTP_MODE=development` permet de conserver le flux MFA/validation OTP sans bloquer l'accès quand aucun SMTP n'est disponible : le code est alors journalisé au lieu d'échouer.

Le patient doit avoir une **adresse e-mail** sur sa fiche (`patients.email`) ou sur son compte utilisateur lié. À la réservation en ligne, le champ `email` de la requête met à jour la fiche patient.

Notifications RDV par e-mail :

| Événement | E-mail |
|-----------|--------|
| Réservation patient (portail / mobile) | Demande enregistrée |
| Planification staff | Planifié |
| Confirmation | Confirmé |
| Report (changement de date) | Reporté (ancienne + nouvelle date) |
| Autre modification (motif, médecin, etc.) | Modifié |
| Annulation | Annulé (+ motif) |
| Rappel J-1 | Rappel veille |

Échec SMTP journalisé, sans bloquer l’API.

**Rappel J-1** (veille du rendez-vous, RDV planifiés ou confirmés du lendemain) :

```powershell
.\.venv\Scripts\python.exe manage.py envoyer_rappels_rdv
# Simulation :
.\.venv\Scripts\python.exe manage.py envoyer_rappels_rdv --dry-run
```

Planifier une exécution quotidienne (ex. 18h, fuseau `TIME_ZONE` du `.env`) :

- **Windows** : Planificateur de tâches → `manage.py envoyer_rappels_rdv`
- **Linux / Docker** : cron `0 18 * * * cd /app && python manage.py envoyer_rappels_rdv`

Chaque RDV n’est rappelé qu’**une fois** (`rappel_j1_envoye_le` sur la fiche).

**Facturation** : e-mail patient à la **validation** de facture et à chaque **paiement** (partiel ou total).

**MFA staff** : e-mail de confirmation à l’utilisateur lors de l’activation MFA (`/auth/mfa/enable/`), si `User.email` est renseigné.

**Push mobile patient** : `PUSH_NOTIFICATIONS_ENABLED`, `FCM_SERVER_KEY` (optionnel). Boîte in-app + envoi FCM pour RDV / factures. Voir `mobile/README.md`.

---

## 7. Dépannage

| Erreur | Cause | Action |
|--------|-------|--------|
| `connection refused` PostgreSQL | Docker arrêté | `docker compose up -d db` |
| Migrations en conflit | Ancienne base | `docker compose down -v` (efface données) puis recommencer |
| CORS bloqué | Origine non listée | Ajouter URL frontend dans `.env` |
| Mobile ne joint pas l’API | URL locale | Utiliser IP LAN ou URL publique |

---

*Voir aussi [README.md](../README.md) à la racine du projet.*
