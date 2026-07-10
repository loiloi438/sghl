# Hébergement et lien démo — SGHL

Guide pour obtenir une **URL publique** (livrable CDC).

---

## Option A — Railway (recommandé étudiant)

1. Créer un compte sur [railway.app](https://railway.app).
2. Nouveau projet → **Deploy from GitHub** (pousser le repo SGHL).
3. Ajouter un service **PostgreSQL** (plugin Railway).
4. Ajouter un service depuis le `Dockerfile` racine.
5. Variables d’environnement :

```env
DEBUG=False
SECRET_KEY=<générer>
JWT_SECRET=<générer>
ALLOWED_HOSTS=*.railway.app
DB_ENGINE=postgresql
DB_HOST=${PGHOST}
DB_PORT=${PGPORT}
DB_NAME=${PGDATABASE}
DB_USER=${PGUSER}
DB_PASSWORD=${PGPASSWORD}
```

6. URL générée : `https://<projet>.up.railway.app/api/v1/sante/`

**Frontend :** déployer `frontend/dist` sur Railway Static ou Vercel avec `VITE_API_BASE_URL` pointant vers l’API.

---

## Option B — Render

1. [render.com](https://render.com) → Web Service → Docker.
2. Base PostgreSQL managée Render.
3. Static Site pour le dossier `frontend/dist`.

---

## Option C — Démo locale (soutenance sur place)

| Service | URL |
|---------|-----|
| API | http://127.0.0.1:8000/api/v1/docs |
| Staff | http://localhost:5173 |
| Santé | http://127.0.0.1:8000/api/v1/sante/ |

```powershell
docker compose up -d --build
cd frontend; npm run dev
```

---

## À renseigner dans le README après déploiement

```markdown
## Démo en ligne

- API : https://VOTRE-URL/api/v1/sante/
- Staff : https://VOTRE-URL-STAFF/
- Swagger : https://VOTRE-URL/api/v1/docs
```

---

*Déploiement détaillé : [DEPLOIEMENT.md](DEPLOIEMENT.md)*
