# Manuel utilisateur — Interface web staff (SGHL)

Guide pour le personnel hospitalier connecté sur **http://localhost:5173** (développement).

---

## 1. Connexion

1. Ouvrir l’application web staff.
2. Saisir **identifiant** et **mot de passe**.
3. Si le compte a le **MFA** activé, saisir le code à 6 chiffres (Google Authenticator).
4. Cliquer sur **Se connecter**.

**Activation MFA (admin) :** après connexion, appeler l’API `POST /api/v1/auth/mfa/setup/` puis `POST /api/v1/auth/mfa/enable/` avec le code affiché dans l’application d’authentification.

Les puces « Comptes démo » remplissent automatiquement les champs (démonstration).

| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| Administrateur | `admin` | `Admin@SGHL2026` |
| Médecin | `medecin` | `Medecin@SGHL2026` |
| Infirmier(ère) | `infirmier` | `Infirmier@SGHL2026` |
| Biologiste | `biologiste` | `Biologiste@SGHL2026` |
| Pharmacien | `pharmacien` | `Pharmacien@SGHL2026` |
| Comptable | `comptable` | `Comptable@SGHL2026` |

> Les comptes **patient** sont réservés à l’application mobile.

**Déconnexion :** menu latéral → bouton de déconnexion.

---

## 2. Tableau de bord

Après connexion, le tableau de bord affiche :

- **Patients actifs** (hospitalisations en cours)
- **Rendez-vous du jour**
- **Prescriptions en attente** (brouillons)
- Raccourcis vers les **modules cliniques**
- Liste des **hospitalisations actives**

---

## 3. Modules par rôle

### Tous les rôles cliniques (lecture large)

| Module | Accès typique |
|--------|----------------|
| Patients | Liste, création, modification dossier |
| Hospitalisations | Admissions, sorties, suivi |
| Rendez-vous | Planning, calendrier semaine |

### Médecin

- Créer et **valider** les prescriptions (ordonnance verrouillée après validation)
- Commander des **analyses laboratoire**
- Admettre / faire sortir un patient (selon droits)
- Gérer les **rendez-vous**

### Infirmier(ère)

- Saisir les **constantes vitales**
- Créer des **plans de soins** et **doses planifiées**
- Marquer doses **administrées** ou **omises**
- Consulter les **alertes doses omises**
- Planifier des **rendez-vous**

### Biologiste

- Workflow **laboratoire** : prélèvement → affectation → saisie résultats → validation → publication
- Télécharger le **compte-rendu PDF** signé

### Pharmacien

- Consulter le **stock**, les **alertes rupture** et les **alertes péremption** (lots périmés ou proches)
- **Approvisionner** un médicament (la dispensation est bloquée si le lot est périmé)
- Préparer et **dispenser** les ordonnances validées

### Comptable

- Consulter les **tarifs**
- **Générer** une facture depuis une hospitalisation
- **Valider** la facture (écriture comptable automatique)
- Enregistrer un **paiement partiel** ou **total**, avec **tiers payant** (CNSS, mutuelle…)
- Consulter le **journal comptable** append-only lié à la facture
- Télécharger la **facture PDF**

### Administrateur

- Accès à tous les modules ci-dessus
- **Journal d’audit** (`/audit`) : historique des actions sensibles
- Gestion **logistique** (bâtiments, services, chambres, lits)

---

## 4. Parcours types

### Admission d’un patient

1. **Patients** → créer ou sélectionner un dossier (consentement obligatoire).
2. **Hospitalisations** → **Admission** : choisir patient, lit libre, motif, médecin référent.
3. Le lit passe au statut **occupé**.

### Prescription médicale

1. Ouvrir une **hospitalisation active**.
2. **Prescriptions** → nouvelle prescription (brouillon).
3. Ajouter diagnostics CIM-10 et **lignes** (médicament, posologie).
4. **Valider** la prescription → déclenchement côté pharmacie.

### Analyse laboratoire

1. **Laboratoire** → nouvelle commande sur une hospitalisation.
2. Enchaîner : prélèvement → affectation biologiste → résultats → validation → publication.
3. Le patient voit les résultats publiés sur l’app mobile.

### Facturation

1. **Facturation** → hospitalisations à facturer.
2. **Générer** la facture (lignes auto séjour / labo / pharma).
3. **Valider** puis enregistrer le **paiement**.

### Rendez-vous

1. **Rendez-vous** → calendrier de la semaine (cliquer un jour).
2. **Nouveau rendez-vous** : patient, médecin, date/heure, motif.
3. Actions : confirmer, terminer, absent, annuler.

---

## 5. Bonnes pratiques

- En cas d’erreur **409** : actualiser la page et réessayer (conflit de version).
- Ne pas partager les comptes : chaque action est tracée dans l’**audit**.
- Vérifier le **consentement données** à la création du patient.
- Après validation d’une prescription, elle n’est plus modifiable.

---

## 6. Support technique

- API : `http://127.0.0.1:8000/api/v1/`
- Documentation API : [API.md](API.md)
- Problème de connexion : vérifier que Django (`runserver`) et Vite (`npm run dev`) sont lancés.

---

*SGHL — Manuel staff v1.0*
