# Écarts et choix techniques — SGHL vs cahier des charges

Document pour la soutenance : transparence sur les écarts assumés et les évolutions prévues.

---

## Conformité forte (livrée)

| Exigence CDC | Réalisation |
|--------------|-------------|
| ERP Web + Mobile | Django Ninja + Vue 3 + Flutter |
| PostgreSQL + verrou optimiste | Config + migrations + champ `version` |
| Parcours patient complet | Hospitalisation → prescriptions → labo → pharma → facturation |
| JWT + rotation refresh | `accounts/jwt_service.py` |
| Audit trail | `audit_auditlog` |
| RBAC 7 rôles | Contrôles API par module |
| LIS workflow | 6 étapes jusqu’à publication |
| PDF signés | `documents` + vérification publique |
| DAT, MCD, MLD, API | Dossier `docs/` |
| CI | GitHub Actions |

---

## Écarts documentés (justification jury)

### Frontend : Tailwind CSS

**CDC :** Vue.js 3 + **Tailwind CSS**.  
**Réalisé :** Vue 3 + **design system CSS custom** (palette médicale bleu/vert, composants type dashboard).  
**Justification :** Livraison plus rapide d’une UI cohérente et responsive ; migration Tailwind possible sans changer l’API.

### API async Django Ninja

**CDC :** API REST typée **async**.  
**Réalisé :** Endpoints **synchrones** (suffisant pour charge démo / soutenance).  
**Justification :** Pas de goulot identifié ; async = optimisation phase 2.

### Monitoring ELK / Prometheus / Grafana

**CDC :** Stack complète.  
**Réalisé :** `GET /sante/` + logs Django.  
**Justification :** Hors périmètre MVP académique ; prêt pour branchement Prometheus.

### Redis pour KPI dashboard

**CDC :** Stats dynamiques via Redis.  
**Réalisé :** Agrégations SQL directes (`/dashboard/stats/`).  
**Justification :** Même résultat fonctionnel à l’échelle démo.

### Mobile : push, chat, rappels

**CDC :** Notifications push, chat temps réel, rappels médicamenteux.  
**Réalisé :** Boîte notifications in-app + enregistrement appareil + FCM (si `FCM_SERVER_KEY`) ; push RDV / facturation ; jeton dev sans Firebase.  
**Écart :** Chat temps réel, rappels médicamenteux programmés, FCM natif Flutter (nécessite `google-services.json`).

### Imagerie médicale

**CDC :** Archivage PDF/imagerie.  
**Réalisé :** PDF métier (facture, ordonnance, CR labo) uniquement.  
**Justification :** PACS / DICOM hors scope court.

### HL7 / FHIR / APIs assurances

**CDC :** Évolutivité interop.  
**Réalisé :** Non.  
**Justification :** Roadmap post-MVP.

---

## Écarts partiellement comblés (cette phase)

| Exigence | État |
|----------|------|
| MFA | TOTP via `pyotp` — setup/enable + login |
| Péremption pharmacie | `date_peremption` + alertes API |
| Paiements partiels / tiers-payant | `montant_paye`, `tiers_payant_*`, statut `partiellement_payee` |
| Journal comptable immuable | `EcritureComptable` append-only |
| Module RH (formations, certifications, planning gardes) | App `rh` + API `/rh/*` + écran Formation & RH |

---

## Recommandation oral jury

> « Le CDC décrit une cible industrielle ; notre livrable couvre le **cœur métier hospitalier** avec traçabilité, sécurité de base et documentation complète. Les écarts (Tailwind, async, push, HL7) sont explicitement listés avec une feuille de route. »

---

*Voir [ROADMAP.md](ROADMAP.md) pour le suivi des tâches.*
