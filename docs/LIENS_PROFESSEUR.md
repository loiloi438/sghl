# SGHL — Liens pour évaluation (professeur)

## Portail web staff (secrétaire, admin, médecin…)

- **URL :** https://sghl-staff.onrender.com
- **Admin :** `tresormouanga` + mot de passe défini sur Render
- **Secrétaire démo :** `samantha` / `Secretaire@SGHL2026`

> Première connexion admin : code MFA envoyé par e-mail (`mouangatresor673@gmail.com`).

## Portail patient web (Human-Care — inscription + espace patient)

- **URL :** https://sghl-staff.onrender.com → onglet **Créer un compte patient**
- **Patient démo (sans inscription) :** `patient` / `Patient@SGHL2026`

## Application mobile patient (Flutter)

- **URL web (navigateur mobile / PC) :** https://sghl-patient.onrender.com
- **APK Android (optionnel) :** construire avec  
  `.\scripts\build_apk.ps1 -ApiBaseUrl "https://sghl-api.onrender.com/api/v1"`

Comptes mobile identiques au portail patient.

## API (healthcheck)

- https://sghl-api.onrender.com/healthz/

## Notes Render (plan gratuit)

- Le serveur **s’endort** après ~15 min d’inactivité → premier accès lent (30–60 s).
- Ouvrir d’abord `/healthz/` si la connexion semble bloquée.

## Variables à vérifier sur Render (`sghl-api`)

- `EMAIL_HOST_PASSWORD` = mot de passe d **application** Google (16 caractères, sans espaces)
- `OTP_MODE=production`
- Test SMTP : `python manage.py test_smtp --to=mouangatresor673@gmail.com`
