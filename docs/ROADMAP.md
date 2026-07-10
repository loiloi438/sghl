# Roadmap SGHL — Suivi cahier des charges

## Priorité 1 — Soutenance

| Statut | Tâche | Fichier / action |
|--------|--------|------------------|
| ✅ | Manuel staff | `docs/MANUEL_STAFF.md` |
| ✅ | Manuel patient | `docs/MANUEL_PATIENT.md` |
| ✅ | Rapport QA / sécurité | `docs/RAPPORT_QA_SECURITE.md` |
| ✅ | Guide PostgreSQL + Docker | `docs/DEPLOIEMENT.md`, `Dockerfile` |
| ✅ | Dépôt git initialisé | `git init` — commit + push à faire par l'équipe |
| ✅ | Script build APK | `scripts/build_apk.ps1` |
| ✅ | Guide hébergement | `docs/HEBERGEMENT.md` |
| ✅ | Export PDF dossier doc | `scripts/export_docs.ps1` |
| ✅ | Écarts CDC documentés | `docs/ECARTS_CDC.md` |

## Priorité 2 — CDC renforcé

| Statut | Tâche |
|--------|--------|
| ✅ | MFA TOTP (`pyotp`, `/auth/mfa/setup/`, `/auth/mfa/enable/`) |
| ✅ | Tests E2E Playwright (`frontend/e2e/login.spec.js`) |
| ✅ | Péremption pharmacie (`date_peremption`, `/pharmacie/stock/peremption/`) |
| ✅ | Paiements partiels / tiers-payant + journal comptable |
| ⬜ | Tailwind (écart assumé — voir `ECARTS_CDC.md`) |

## Priorité 3 — Long terme

| Statut | Tâche |
|--------|--------|
| ✅ | E-mails RDV + rappel J-1 ; facturation (validation / paiement) ; alerte MFA activé |
| ✅ | Push notifications (inbox + FCM optionnel, app mobile) |
| ✅ | Module RH — formations, certifications, planning gardes (`rh/`, `/rh/*`) |
| ✅ | Modules backend complémentaires — assurance, inventaire, urgences, paramètres, téléconsultation |
| ✅ | Sécurité backend — bcrypt, rate limit API, auth paiements, `/sante/` enrichi |
| ⬜ | Imagerie médicale |
| ⬜ | Redis / ELK / Prometheus |
| ⬜ | HL7 / FHIR |

## Priorité 4 — Mobile & responsive (cahier des charges)

### Objectif principal

Livrer une application Flutter patient responsive, sécurisée, connectée à l’API Django et alignée sur le parcours de soins décrit dans le cahier des charges.

### Jalons recommandés

1. **MVP mobile patient**
   - Authentification sécurisée avec JWT/MFA
   - Tableau de bord patient
   - Prise de rendez-vous
   - Historique médical et documents PDF
   - Notifications in-app et rappels

2. **Fonctionnalités de suivi clinique**
   - Plan de soins et observance
   - Résultats laboratoire consultables
   - Factures et paiements partiels
   - Suivi post-hospitalisation

3. **Expérience mobile complète**
   - Navigation responsive et adaptée tablette/téléphone
   - Notifications push réelles via FCM
   - Chat temps réel et messages hospitaliers
   - Synchronisation fiable des données et gestion des erreurs réseau

4. **Qualité & conformité**
   - Tests unitaires / widget / E2E sur le flux mobile
   - Audit trail côté API et journalisation mobile
   - Respect RGPD, confidentialité et traçabilité d’accès

### Périmètre prioritaire actuel

- Authentification et profil patient
- Prise et consultation des rendez-vous
- Documents, factures et résultats
- Notifications et rappels médicaux
- Interface web responsive pour les vues critiques du parcours patient
