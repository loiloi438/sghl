# Checklist de finalisation — application mobile SGHL

## 1. Fonctionnement de base
- [ ] L’application démarre sans crash sur Android/iOS
- [ ] La connexion et la déconnexion fonctionnent correctement
- [ ] La session persiste et la réouverture de l’application redirige vers le bon écran
- [ ] Les écrans principaux se chargent avec les états loading / erreur / vide

## 2. Parcours patient critique
- [ ] Tableau de bord patient lisible et utile
- [ ] Rendez-vous : consultation, création et annulation fonctionnent
- [ ] Prescriptions : affichage, statut et téléchargement PDF fonctionnent
- [ ] Laboratoire : résultats visibles et téléchargeables
- [ ] Factures : montant, statut et PDF visibles
- [ ] Plans de soins et constantes : données compréhensibles et cohérentes

## 3. Expérience utilisateur
- [ ] Navigation claire entre les écrans
- [ ] Messages d’erreur explicites et compréhensibles
- [ ] Feedback utilisateur sur actions importantes (succès, erreur, chargement)
- [ ] Interface adaptée aux petits écrans et au mode sombre

## 4. Intégration API et réseau
- [ ] Les appels API répondent correctement en environnement local et de test
- [ ] Les erreurs réseau sont gérées proprement
- [ ] Les temps d’attente et retries sont raisonnables
- [ ] Les données partielles ou nulles n’entraînent pas de crash

## 5. Sécurité et conformité
- [ ] Les tokens sont stockés et nettoyés correctement
- [ ] Les accès non autorisés sont bloqués
- [ ] Les données sensibles ne sont pas exposées inutilement
- [ ] Les logs ou traces critiques sont conservés si nécessaire

## 6. Qualité et tests
- [ ] Tests unitaires et widget couvrant les écrans clés
- [ ] Vérification des parcours de connexion et rendez-vous
- [ ] Validation sur émulateur ou appareil réel
- [ ] Revue finale des écrans et contenus textuels

## 7. Déploiement
- [ ] Build Android validé
- [ ] Build iOS validé si applicable
- [ ] Variables d’environnement et endpoints configurés
- [ ] Documentation utilisateur et support disponible

## Verdict de prêt
- [ ] MVP fonctionnel prêt pour démonstration
- [ ] Version prête pour validation métier
- [ ] Version prête pour mise en production
