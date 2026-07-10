# SGHL — Interface web (Vue.js 3)

Interface web pour le **personnel hospitalier** et le **portail patient**, connectée à l'API Django Ninja (`/api/v1/`).

## Prérequis

- Node.js 20+
- Backend SGHL en cours d'exécution sur `http://127.0.0.1:8000`

## Démarrage

```powershell
cd frontend
npm install
npm run dev
```

Ouvrir [http://localhost:5173](http://localhost:5173).

Le proxy Vite redirige `/api` vers le backend Django.

## Comptes de démonstration

### Personnel (MFA par e-mail à la connexion)

| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| Médecin | `medecin` | `Medecin@SGHL2026` |
| Infirmier | `infirmier` | `Infirmier@SGHL2026` |
| Pharmacien | `pharmacien` | `Pharmacien@SGHL2026` |
| Comptable | `comptable` | `Comptable@SGHL2026` |
| Biologiste | `biologiste` | `Biologiste@SGHL2026` |
| Admin | `tresormouanga` | *(mot de passe défini au seed)* |

> Les comptes staff avec MFA activé reçoivent un code par e-mail après le mot de passe (HTTP 202 → saisie du code).

### Patients (portail web `/patient`)

1. **Inscription** depuis la page de connexion (« Nouveau patient ? Créez votre compte »).
2. **Validation** du compte par code reçu par e-mail (`/validate-account`).
3. **Connexion** → redirection automatique vers l'espace patient.

Comptes démo seedés : voir `python manage.py seed_demo` (patients `patient1`, `patient2`, …).

## Portail patient

Routes principales :

- `/patient` — tableau de bord (hospitalisation, doses, constantes)
- `/patient/rendez-vous` — prise de RDV (présentiel ou téléconsultation avec lien visio)
- `/patient/soins` — constantes vitales et plan de soins
- `/patient/prescriptions` — ordonnances validées
- `/patient/laboratoire` — résultats d'analyses
- `/patient/factures` — factures et **paiement en ligne** (Stripe)
- `/patient/notifications` — alertes et rappels
- `/patient/profil` — coordonnées et déconnexion

Page publique **Contact & localisation** : `/contact` (accessible sans connexion).

## Modules staff

- **Tableau de bord** — KPI (patients actifs, RDV du jour, prescriptions en attente)
- **Patients** — liste et création
- **Rendez-vous** — calendrier semaine, planification, téléconsultation
- **Hospitalisations** — admissions et sorties
- **Prescriptions** — brouillon, lignes, validation (médecin)
- **Laboratoire** — workflow LIS complet
- **Pharmacie** — stock, ordres de dispensation
- **Facturation** — génération auto, validation, paiement
- **Soins infirmiers** — constantes vitales, alertes doses
- **Téléconsultation**, **Urgences**, **Inventaire**, **Formation RH**, **Contact & localisation**, etc.

## Build production

```powershell
npm run build
```

Les fichiers statiques sont générés dans `dist/`.

Variables utiles (`.env.production`) :

- `VITE_API_BASE_URL` — URL de l'API en production
- `VITE_STRIPE_PUBLISHABLE_KEY` — clé publique Stripe pour le paiement patient

## Tests E2E (Playwright)

```powershell
npm run test:e2e
```

Le scénario staff `e2e/login.spec.js` couvre la connexion médecin → tableau de bord.
