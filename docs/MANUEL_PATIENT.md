# Manuel utilisateur — Application mobile patient (SGHL)

Application **Flutter** pour les patients : consultation du dossier, rendez-vous, résultats et documents.

---

## 1. Prérequis

- Smartphone Android (APK) ou émulateur / simulateur en développement.
- Connexion au serveur SGHL (réseau local ou URL de démo).
- Compte patient créé par l’administration (lié au dossier médical).

**Compte démo :**

| Identifiant | Mot de passe |
|-------------|--------------|
| `patient` | `Patient@SGHL2026` |

---

## 2. Configuration de l’API (développement)

Par défaut, l’app pointe vers l’API Django. Sur émulateur Android, l’URL est souvent `http://10.0.2.2:8000/api/v1/`.

Fichier à adapter si besoin : `mobile/lib/core/api_config.dart`.

---

## 3. Connexion

1. Lancer l’application **SGHL Patient**.
2. Saisir identifiant et mot de passe.
3. Appuyer sur **Se connecter**.

L’écran de connexion propose un raccourci **Compte démo patient** pour les tests.

---

## 4. Écran d’accueil

Après connexion, l’accueil propose des raccourcis :

| Tuile | Contenu |
|-------|---------|
| Constantes vitales | Historique des mesures (TA, température, etc.) |
| Plans de soins | Plans actifs de l’équipe soignante |
| Doses | Médicaments planifiés / administrés |
| Rendez-vous | Prendre ou annuler un RDV |
| Prescriptions | Ordonnances validées |
| Laboratoire | Résultats **publiés** uniquement |
| Factures | Factures et téléchargement PDF |

---

## 5. Rendez-vous

1. Ouvrir **Rendez-vous**.
2. **Nouveau RDV** : choisir un médecin, date/heure, motif.
3. La liste affiche les RDV à venir et passés.
4. **Annuler** un RDV planifié ou confirmé (selon règles métier).

> Les créneaux en conflit avec un autre RDV du même médecin sont refusés par le système.

---

## 6. Documents PDF

Sur les écrans **Prescriptions**, **Laboratoire** ou **Factures**, utiliser le bouton de **téléchargement PDF**.

Les documents sont **signés électroniquement** ; un code de vérification permet de contrôler l’authenticité via le site staff (endpoint public de vérification).

---

## 7. Sécurité et confidentialité

- Ne communiquez jamais votre mot de passe.
- Déconnectez-vous sur un appareil partagé.
- Seuls les **résultats publiés** par le laboratoire sont visibles.
- Vos accès sont journalisés côté serveur (audit).

---

## 8. Dépannage

| Problème | Solution |
|----------|----------|
| « Erreur réseau » | Vérifier Wi‑Fi et que le serveur Django tourne |
| Login refusé | Utiliser un compte `patient`, pas un compte staff |
| Liste vide | Données non encore saisies par l’hôpital ou non publiées |

---

## 9. Build APK (technique)

Voir [DEPLOIEMENT.md](DEPLOIEMENT.md) ou exécuter :

```powershell
cd mobile
flutter build apk --release
```

APK généré : `mobile/build/app/outputs/flutter-apk/app-release.apk`

---

*SGHL — Manuel patient v1.0*
