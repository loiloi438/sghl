# Rapport QA & Sécurité — SGHL

**Projet :** Système de Gestion Hospitalière et de Laboratoire  
**Version :** 1.0.0  
**Date :** juin 2026  

---

## 1. Objectif

Ce document résume les activités de **contrôle qualité** et les mesures de **sécurité** implémentées, ainsi que les écarts connus par rapport au cahier des charges.

---

## 2. Périmètre testé

| Composant | Méthode | Statut |
|-----------|---------|--------|
| API Django (`/api/v1/`) | Tests unitaires / API (Django TestCase + Ninja TestClient) | ✅ 24 tests OK |
| Modèles & règles métier | Tests hospitalisation, RDV, prescriptions, labo, etc. | ✅ Couvert |
| Build frontend Vue | `npm run build` + CI GitHub Actions | ✅ OK |
| Application mobile Flutter | `flutter analyze` (manuel) | ✅ Analyse statique OK |
| Tests E2E navigateur | — | ❌ Non réalisés |
| Tests de charge | — | ❌ Non réalisés |
| Audit intrusion | — | ❌ Non réalisés |

**Commande de reproduction :**

```powershell
.\.venv\Scripts\python.exe manage.py test
cd frontend; npm run build
```

---

## 3. Synthèse des tests automatisés

| Module | Tests | Exemples validés |
|--------|-------|------------------|
| core | Health check API | `GET /sante/` |
| accounts | Rate limit login | Blocage après 5 échecs |
| patients | CRUD patient | Création, consentement |
| hospitalisation | Admission / sortie | Contrainte lit, version |
| rendezvous | Workflow RDV | Créer, confirmer, annuler, API semaine |
| prescriptions | Prescription | Brouillon, validation |
| laboratoire | LIS | Workflow commande |
| pharmacie | Stock / dispensation | — |
| facturation | Facture | Génération, validation |
| documents | PDF | Signature / empreinte |
| soins | Constantes, doses | — |

**Taux de réussite observé :** 24/24 (100 % sur la suite actuelle).

---

## 4. Sécurité — mesures en place

| Exigence CDC | Implémentation | Preuve |
|--------------|----------------|--------|
| Authentification JWT | Access + refresh, rotation refresh | `accounts/jwt_service.py` |
| RBAC | 7 rôles, contrôles par endpoint | `api/v1/*.py` |
| Audit trail | User, timestamp, IP, old/new JSON | `audit/models.py` |
| Mots de passe forts | Validateurs Django (min 10 car.) | `settings.py` |
| Rate limiting login | 5 tentatives / 15 min / IP+user | `accounts/rate_limit.py` |
| CORS production | Liste blanche `CORS_ALLOWED_ORIGINS` | `settings.py` |
| Verrouillage optimiste | Champ `version`, HTTP 409 | Modèles métier |
| PDF signés | SHA-256 + HMAC, code vérification | `documents/` |
| Isolation patient | Portail `/patient/*`, rôle patient | `patient_portal.py` |

---

## 5. Écarts sécurité (connus)

| Exigence CDC | État | Risque | Mitigation prévue |
|--------------|------|--------|-------------------|
| MFA (2FA) | Champ `mfa_enabled` sans TOTP | Moyen | Phase 2 : django-otp |
| HTTPS | Non forcé en dev | Faible en local | Reverse proxy prod (nginx) |
| Bcrypt explicite | PBKDF2 Django par défaut | Faible | Acceptable pour démo |
| AES-256 global | Non (HMAC PDF seulement) | Faible | Chiffrement disque / TLS |
| Antivirus uploads | Non | Moyen | Scan ClamAV si uploads étendus |
| Tests intrusion | Non | — | Checklist OWASP manuelle |

---

## 6. Règles métier validées

- Une seule **hospitalisation active** par patient et par lit (contraintes DB).
- **Prescription** non modifiable après validation.
- **Commande labo** verrouillée après validation / publication.
- **Chevauchement RDV** refusé pour un même médecin.
- **Compte patient** isolé du staff web.
- **Consentement** requis à la création du dossier patient.

---

## 7. CI / qualité continue

Pipeline `.github/workflows/ci.yml` :

- Job **backend** : `pip install` + `manage.py test` (SQLite CI)
- Job **frontend** : `npm ci` + `npm run build`

Déclenché sur push / pull request (`main`, `master`, `develop`).

---

## 8. Recommandations avant mise en production

1. `DEBUG=False`, secrets forts (`SECRET_KEY`, `JWT_SECRET`).
2. Base **PostgreSQL** (pas SQLite).
3. **HTTPS** obligatoire (Let’s Encrypt).
4. Sauvegardes quotidiennes PostgreSQL.
5. Activer **MFA** pour les comptes admin.
6. Ajouter tests **E2E** (login + admission + prescription).
7. Journaliser les accès aux dossiers patients (extension audit).

---

## 9. Conclusion

Le SGHL atteint un niveau **suffisant pour une démonstration académique** : cœur métier testé, sécurité de base (JWT, RBAC, audit, rate limit), documentation complète (DAT, MCD, MLD, API).

Les travaux restants concernent surtout la **mise en production** (HTTPS, PostgreSQL prod, MFA) et les tests **E2E / charge**, conformément au périmètre « entreprise » du CDC.

---

*Rapport rédigé pour le livrable « Supports — rapports QA/Sécurité ».*
