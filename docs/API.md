# Dictionnaire API — SGHL v1

Contrat REST du **Système de Gestion Hospitalière et de Laboratoire**, conforme au livrable CDC « dictionnaires API ».

| Élément | Valeur |
|---------|--------|
| Base URL | `http://localhost:8000/api/v1/` |
| Format | JSON (`Content-Type: application/json`) |
| Version | `1.0.0` |
| Spécification machine | [openapi.json](openapi.json) |
| UI interactive | `http://localhost:8000/api/v1/docs` (Swagger, serveur Django lancé) |

---

## 1. Authentification

### Obtenir un jeton

```http
POST /api/v1/auth/login/
```

**Corps :**

```json
{ "username": "medecin", "password": "Medecin@SGHL2026" }
```

**Réponse 200 :**

```json
{
  "access_token": "<JWT>",
  "refresh_token": "<opaque>",
  "token_type": "Bearer"
}
```

**Erreurs :** `401` identifiants invalides · `429` trop de tentatives (rate limit).

### Appels authentifiés

```http
Authorization: Bearer <access_token>
```

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/auth/login/` | POST | Non | Connexion staff ou patient |
| `/auth/refresh/` | POST | Non | Rotation refresh → nouveaux jetons |
| `/auth/logout/` | POST | Non | Révoque le refresh token (corps : `refresh_token`) |
| `/auth/me/` | GET | Oui | Profil utilisateur connecté |

**Règle staff web :** les comptes `patient` sont refusés sur l’interface Vue (réservés au mobile).

---

## 2. Conventions communes

### Pagination

Les listes paginées renvoient :

```json
{
  "items": [ ... ],
  "count": 42
}
```

Paramètres query : `limit`, `offset` (Django Ninja Pagination).

### Verrouillage optimiste

Les actions de modification sur entités versionnées exigent le champ **`version`** dans le corps (ex. confirmer un RDV, valider une prescription). En cas de conflit : **`409`** avec message explicite.

### Codes HTTP usuels

| Code | Signification |
|------|----------------|
| 200 | Succès |
| 400 | Données invalides |
| 401 | Jeton absent ou expiré |
| 403 | Rôle insuffisant |
| 404 | Ressource introuvable |
| 409 | Conflit de version ou règle métier (créneau RDV, lit occupé…) |
| 429 | Rate limit login |

### Rôles (RBAC)

`admin` · `medecin` · `infirmier` · `biologiste` · `pharmacien` · `comptable` · `patient`

Chaque module applique des ensembles de rôles (`ROLES_LECTURE`, `ROLES_GESTION`, etc.) dans le code `api/v1/`.

---

## 3. Santé & pilotage

| Endpoint | Méthode | Auth | Rôles | Description |
|----------|---------|------|-------|-------------|
| `/sante/` | GET | Non | — | Monitoring CDC (statut API) |
| `/dashboard/stats/` | GET | Oui | Staff | KPI : patients actifs, RDV jour, prescriptions en attente |
| `/audit/logs/` | GET | Oui | Admin | Journal d’audit (filtres query) |

---

## 4. Patients

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/patients/` | GET | Oui | Liste paginée des dossiers |
| `/patients/` | POST | Oui | Création patient (`consentement_donnees` requis) |
| `/patients/{patient_id}/` | GET | Oui | Détail dossier |
| `/patients/{patient_id}/` | PATCH | Oui | Mise à jour (champ `version`) |

---

## 5. Logistique

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/logistique/batiments/` | GET, POST | Oui | Bâtiments |
| `/logistique/services/` | GET, POST | Oui | Services (`?batiment_id=`) |
| `/logistique/chambres/` | GET, POST | Oui | Chambres (`?service_id=`) |
| `/logistique/lits/` | GET, POST | Oui | Lits (`?chambre_id=`, `?statut=`) |
| `/logistique/lits/{lit_id}/statut/` | PATCH | Oui | Changer statut lit (`version`) |

---

## 6. Hospitalisation

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/hospitalisations/` | GET | Oui | Liste (filtre `statut`) |
| `/hospitalisations/actives/` | GET | Oui | Hospitalisations en cours |
| `/hospitalisations/admission/` | POST | Oui | Admission patient + lit (`lit_version`) |
| `/hospitalisations/{id}/` | GET | Oui | Détail |
| `/hospitalisations/{id}/historique/` | GET | Oui | Historique du patient lié |
| `/hospitalisations/{id}/sortie/` | POST | Oui | Sortie + libération lit (`version`) |

---

## 7. Rendez-vous

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/rendez-vous/stats/` | GET | Oui | Compteurs RDV |
| `/rendez-vous/semaine/` | GET | Oui | Calendrier 7 jours (`?date=YYYY-MM-DD`) |
| `/rendez-vous/medecins/` | GET | Oui | Liste médecins actifs |
| `/rendez-vous/` | GET | Oui | Liste (`?date=`, `?statut=`, `?medecin_id=`) |
| `/rendez-vous/` | POST | Oui | Planifier un RDV |
| `/rendez-vous/{rdv_id}/` | GET | Oui | Détail |
| `/rendez-vous/{rdv_id}/confirmer/` | POST | Oui | Confirmer (`version`) |
| `/rendez-vous/{rdv_id}/annuler/` | POST | Oui | Annuler (`version`, `motif_annulation`) |
| `/rendez-vous/{rdv_id}/terminer/` | POST | Oui | Terminer (`version`) |
| `/rendez-vous/{rdv_id}/absent/` | POST | Oui | Marquer absent (`version`) |

---

## 8. Prescriptions

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/diagnostics-cim10/` | GET | Oui | Référentiel CIM-10 (`?q=` recherche) |
| `/hospitalisations/{id}/prescriptions/` | GET, POST | Oui | Liste / création brouillon |
| `/prescriptions/{id}/` | GET, PATCH | Oui | Détail / modifier brouillon |
| `/prescriptions/{id}/lignes/` | POST | Oui | Ajouter ligne médicament |
| `/prescriptions/{id}/valider/` | POST | Oui | Valider (`version`) → verrouillage |
| `/prescriptions/{id}/pdf/` | GET | Oui | Télécharger ordonnance PDF signée |

---

## 9. Soins infirmiers

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/hospitalisations/{id}/constantes-vitales/` | GET, POST | Oui | Constantes vitales |
| `/hospitalisations/{id}/plans-soins/` | GET, POST | Oui | Plans de soins |
| `/hospitalisations/{id}/interventions/` | GET, POST | Oui | Interventions infirmières |
| `/plans-soins/{plan_id}/doses/` | GET, POST | Oui | Doses planifiées |
| `/doses/{dose_id}/administrer/` | POST | Oui | Administrer dose (`version`) |
| `/doses/{dose_id}/omission/` | POST | Oui | Marquer omise (`version`) |
| `/soins/alertes/doses-omises/` | GET | Oui | Alertes doses en retard |

---

## 10. Laboratoire (LIS)

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/analyses-catalogue/` | GET | Oui | Catalogue analyses |
| `/hospitalisations/{id}/commandes-analyses/` | GET, POST | Oui | Commandes labo |
| `/commandes-analyses/{id}/` | GET | Oui | Détail commande |
| `/commandes-analyses/{id}/prelevement/` | POST | Oui | Étape prélèvement |
| `/commandes-analyses/{id}/affectation/` | POST | Oui | Affectation biologiste |
| `/commandes-analyses/{id}/resultats/` | POST | Oui | Saisie résultats |
| `/commandes-analyses/{id}/valider/` | POST | Oui | Validation biologiste |
| `/commandes-analyses/{id}/publier/` | POST | Oui | Publication patient |
| `/commandes-analyses/{id}/pdf/` | GET | Oui | Compte-rendu PDF signé |

**Workflow statuts :** `commandee` → `prelevee` → `affectee` → `resultats_saisis` → `validee` → `publiee`.

---

## 11. Pharmacie

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/pharmacie/stock/` | GET | Oui | Stock médicaments |
| `/pharmacie/stock/alertes/` | GET | Oui | Stock sous seuil |
| `/pharmacie/stock/{id}/approvisionner/` | POST | Oui | Réapprovisionnement |
| `/pharmacie/prescriptions-a-dispenser/` | GET | Oui | Prescriptions validées sans ordre |
| `/pharmacie/ordres-dispensation/` | GET | Oui | Ordres en cours |
| `/pharmacie/ordres-dispensation/` | POST | Oui | Créer ordre depuis prescription |
| `/pharmacie/ordres-dispensation/{id}/` | GET | Oui | Détail ordre |
| `/pharmacie/ordres-dispensation/{id}/preparer/` | POST | Oui | Préparer (`version`) |
| `/pharmacie/ordres-dispensation/{id}/dispenser/` | POST | Oui | Dispenser + décrément stock |

---

## 12. Facturation

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/facturation/tarifs/` | GET | Oui | Grille tarifaire |
| `/facturation/hospitalisations-a-facturer/` | GET | Oui | Séjours sans facture |
| `/facturation/factures/` | GET | Oui | Liste factures |
| `/facturation/factures/{id}/` | GET | Oui | Détail facture + lignes |
| `/hospitalisations/{id}/facture/` | GET | Oui | Facture du séjour |
| `/hospitalisations/{id}/facture/generer/` | POST | Oui | Génération auto des lignes |
| `/facturation/factures/{id}/valider/` | POST | Oui | Valider (`version`) |
| `/facturation/factures/{id}/paiement/` | POST | Oui | Enregistrer paiement |
| `/facturation/factures/{id}/pdf/` | GET | Oui | Facture PDF signée |

---

## 13. Documents

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/documents/verifier/{code}/` | GET | Non | Vérification authenticité PDF (`code_verification`) |

---

## 14. Portail patient (Flutter)

Préfixe logique **`/patient/`** — compte `role=patient` uniquement.

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/patient/profil/` | GET | Profil patient lié au compte |
| `/patient/tableau-de-bord/` | GET | Synthèse accueil mobile |
| `/patient/constantes-vitales/` | GET | Historique constantes |
| `/patient/plans-soins/` | GET | Plans de soins |
| `/patient/doses/` | GET | Doses planifiées |
| `/patient/prescriptions/` | GET | Ordonnances |
| `/patient/resultats-laboratoire/` | GET | Résultats publiés |
| `/patient/factures/` | GET | Factures du patient |
| `/patient/rendez-vous/medecins/` | GET | Médecins disponibles |
| `/patient/rendez-vous/` | GET, POST | Liste / prise de RDV |
| `/patient/rendez-vous/{id}/annuler/` | POST | Annulation RDV (`version`) |

---

## 15. Schémas principaux (extraits)

Les schémas complets sont dans **OpenAPI** (`components.schemas`). Exemples :

### `TokenOut`

| Champ | Type |
|-------|------|
| access_token | string |
| refresh_token | string |
| token_type | string (défaut `Bearer`) |

### `PatientOut`

| Champ | Type |
|-------|------|
| id | UUID |
| numero_dossier | string |
| nom, prenom | string |
| date_naissance | date |
| sexe | string |
| version | integer |

### `RendezVousOut`

| Champ | Type |
|-------|------|
| id | UUID |
| patient_id | UUID |
| medecin_id | integer |
| date_heure | datetime ISO |
| statut | string |
| version | integer |

---

## 16. Maintenance du dictionnaire

Régénérer OpenAPI après modification des routes :

```powershell
.\.venv\Scripts\python.exe manage.py export_openapi
```

Fichier produit : `docs/openapi.json` (81 chemins au dernier export).

Consulter la doc interactive :

```powershell
.\.venv\Scripts\python.exe manage.py runserver
# → http://127.0.0.1:8000/api/v1/docs
```

---

## 17. Correspondance livrables CDC

| Livrable CDC | Fichier SGHL |
|--------------|--------------|
| Dictionnaire API | Ce document + `openapi.json` |
| Versioning `/api/v1/` | Préfixe URL + `info.version` OpenAPI |
| Monitoring | `GET /sante/` |
| Sécurité JWT | Section 1 + `auth_backend.py` |

---

*Documentation alignée sur le code `api/v1/` — juin 2026.*
