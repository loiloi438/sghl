# Planification sprint — application mobile SGHL

## Objectif global

Livrer un MVP mobile patient sécurisé, responsive et connecté à l’API SGHL, centré sur le parcours de soins : authentification, tableau de bord, rendez-vous, documents, résultats, factures et notifications.

## Principe de priorisation

- Priorité 1 : parcours patient critique et utile
- Priorité 2 : fiabilité réseau et sécurité
- Priorité 3 : expérience mobile complète et notifications
- Priorité 4 : qualité, tests et conformité

---

## Sprint 0 — Alignement technique et préparation

### Objectif

Valider les intégrations API, la configuration réseau et les flux de base avant développement.

### User stories
- En tant qu’utilisateur, je peux me connecter à l’application mobile avec un compte autorisé.
- En tant que développeur, je peux appeler les endpoints patient sans erreurs de contrat.

### Tâches
- Vérifier les endpoints existants dans [mobile/lib/services/patient_services.dart](mobile/lib/services/patient_services.dart).
- Valider la configuration d’API dans [mobile/lib/core/api_config.dart](mobile/lib/core/api_config.dart).
- Définir les erreurs réseau, les états de chargement et les messages utilisateur.
- Préparer la structure de navigation et les écrans prioritaires.

### Critères d’acceptation
- Les écrans principaux démarrent sans crash.
- Les erreurs réseau sont affichées proprement.
- Les flux auth et session sont cohérents.

---

## Sprint 1 — Authentification, dashboard et navigation

### Objectif

Stabiliser le socle utilisateur de l’application mobile et livrer un premier parcours patient cohérent.

### User stories
- En tant que patient, je peux me connecter et me déconnecter.
- En tant que patient, je peux consulter mon tableau de bord principal.
- En tant que patient, je peux naviguer rapidement entre les écrans clés.

### Tâches
- Finaliser le flux de connexion dans [mobile/lib/screens/login_screen.dart](mobile/lib/screens/login_screen.dart).
- Optimiser l’écran d’accueil dans [mobile/lib/screens/home_screen.dart](mobile/lib/screens/home_screen.dart).
- Ajouter des états vides, loading et erreurs sur les écrans principaux.
- Ajouter un menu de navigation clair et cohérent avec le parcours de soins.
- Vérifier la persistance de session et la déconnexion propre.
- Valider les écrans de suivi déjà enrichis : prescriptions, laboratoire, factures, plans de soins et constantes.

### Critères d’acceptation
- Un patient peut se connecter en moins de 2 clics après ouverture de l’app.
- Le tableau de bord affiche profil, hospitalisation active, rappels et raccourcis.
- Le parcours est stable sur téléphone et tablette.

---

## Sprint 2 — Rendez-vous et suivi clinique

### Objectif

Permettre au patient de gérer son parcours de prise de rendez-vous.

### User stories
- En tant que patient, je peux consulter mes rendez-vous à venir.
- En tant que patient, je peux prendre un rendez-vous avec un médecin disponible.
- En tant que patient, je peux annuler un rendez-vous si nécessaire.

### Tâches
- Finaliser l’écran [mobile/lib/screens/rendez_vous_screen.dart](mobile/lib/screens/rendez_vous_screen.dart).
- Améliorer le formulaire de prise de RDV avec validation côté client.
- Ajouter des messages de succès/échec après création ou annulation.
- Gérer les statuts de RDV de manière lisible.
- Prévoir un système de rappel visuel et de notification in-app.
- Vérifier la cohérence de l’affichage des notifications et des rendez-vous dans l’interface mobile.

### Critères d’acceptation
- Un rendez-vous peut être créé en moins de 2 minutes.
- Les erreurs de validation sont explicites.
- Les annulations sont prises en compte immédiatement après synchronisation.

---

## Sprint 3 — Documents, résultats et observance

### Objectif

Rendre l’application utile pour le suivi médical quotidien.

### User stories
- En tant que patient, je peux consulter mes plans de soins et mes doses.
- En tant que patient, je peux voir mes constantes vitales et mes résultats laboratoire.
- En tant que patient, je peux télécharger mes documents et factures PDF.

### Tâches
- Vérifier les écrans [mobile/lib/screens/plans_screen.dart](mobile/lib/screens/plans_screen.dart), [mobile/lib/screens/doses_screen.dart](mobile/lib/screens/doses_screen.dart), [mobile/lib/screens/constantes_screen.dart](mobile/lib/screens/constantes_screen.dart), [mobile/lib/screens/laboratoire_screen.dart](mobile/lib/screens/laboratoire_screen.dart) et [mobile/lib/screens/factures_screen.dart](mobile/lib/screens/factures_screen.dart).
- Ajouter un affichage lisible des données médicales avec filtres et tri.
- Connecter les boutons de téléchargement PDF aux services existants.
- Ajouter un aperçu rapide des éléments importants sur le tableau de bord.

### Critères d’acceptation
- Les documents disponibles sont visibles et téléchargeables.
- Les résultats laboratoire sont consultables de façon claire.
- Les doses et plans de soins sont présentés dans un format mobile adapté.

---

## Sprint 4 — Notifications, qualité et conformité

### Objectif

Rendre l’application prête pour une utilisation réelle, sécurisée et robuste.

### User stories
- En tant que patient, je reçois des notifications utiles sur les rendez-vous et documents.
- En tant que développeur, je peux garantir un comportement stable de l’application.
- En tant que responsable de conformité, je peux suivre les traces d’accès et les événements critiques.

### Tâches
- Finaliser le service de notifications in-app via [mobile/lib/services/notification_inbox_service.dart](mobile/lib/services/notification_inbox_service.dart).
- Préparer l’intégration push réelle via Firebase/FCM.
- Ajouter des tests widget et de bout en bout sur les flux de connexion et RDV.
- Vérifier les messages d’erreur, le mode sombre et les performances globales.
- Documenter les règles d’usage et les points de sécurité mobile.

### Critères d’acceptation
- Les notifications in-app sont fonctionnelles.
- Les principaux flux sont couverts par des tests automatisés.
- L’application respecte les principes de sécurité et de traçabilité du projet.

---

## Livrables de fin de cycle

- Application mobile stable sur Android/iOS
- Parcours patient principal opérationnel
- Notifications et rappels fonctionnels
- Documentation de support et checklist QA mobile

## Recommandation de livraison

Livrer d’abord le parcours patient critique : connexion, tableau de bord, rendez-vous et documents. Les fonctions plus avancées comme le chat temps réel ou la push réelle peuvent être intégrées ensuite, une fois la base stable.
