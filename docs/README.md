# Documentation SGHL

Index des livrables pour la soutenance et le cahier des charges.

| Document | Description |
|----------|-------------|
| [DAT.md](DAT.md) | Architecture technique |
| [MCD.md](MCD.md) | Modèle conceptuel de données |
| [MLD.md](MLD.md) | Modèle logique PostgreSQL |
| [API.md](API.md) | Dictionnaire API REST |
| [openapi.json](openapi.json) | Spécification OpenAPI 3.1 |
| [MANUEL_STAFF.md](MANUEL_STAFF.md) | Manuel interface web |
| [MANUEL_PATIENT.md](MANUEL_PATIENT.md) | Manuel application mobile |
| [RAPPORT_QA_SECURITE.md](RAPPORT_QA_SECURITE.md) | Qualité et sécurité |
| [DEPLOIEMENT.md](DEPLOIEMENT.md) | PostgreSQL, Docker, hébergement |
| [HEBERGEMENT.md](HEBERGEMENT.md) | Déploiement Railway / Render |
| [ECARTS_CDC.md](ECARTS_CDC.md) | Écarts assumés vs cahier des charges |
| [ROADMAP.md](ROADMAP.md) | Suivi des priorités soutenance |

**Export PDF :** ouvrir chaque fichier `.md` dans VS Code / Cursor → Aperçu → Imprimer en PDF, ou utiliser Pandoc :

```powershell
pandoc docs/DAT.md -o docs/DAT.pdf
```
