<template>
  <section class="pub-section pub-legal">
    <p class="pub-eyebrow">RGPD</p>
    <h1 class="pub-section-title">Politique de confidentialité</h1>
    <div class="pub-card pub-legal-body">
      <h3>Données collectées</h3>
      <p>
        Identifiants de compte, coordonnées (e-mail, téléphone), données de parcours de soins
        nécessaires au service (rendez-vous, résultats, factures), et logs techniques de sécurité.
      </p>
      <h3>Finalités</h3>
      <p>
        Fournir le portail patient et les outils staff, sécuriser les accès (JWT, MFA), envoyer
        des notifications utiles (RDV, codes de validation), et améliorer la qualité du service.
      </p>
      <h3>Base légale</h3>
      <p>
        Exécution du service demandé, consentement (inscription patient / cookies techniques
        essentiels), et intérêts légitimes de sécurité.
      </p>
      <h3>Conservation</h3>
      <p>
        Les données sont conservées le temps nécessaire au fonctionnement du compte et aux
        obligations applicables. Les environnements de démo peuvent être réinitialisés.
      </p>
      <h3>Vos droits</h3>
      <p>
        Accès, rectification, opposition et suppression (dans les limites légales) : contactez
        <a href="mailto:info@sghl-sante.com">info@sghl-sante.com</a> ou utilisez le
        <RouterLink to="/contact">formulaire de contact</RouterLink>.
      </p>
      <h3>Sécurité</h3>
      <p>
        Connexions chiffrées (HTTPS), contrôle d’accès par rôle, et mesures anti-abus (rate limit).
        Voir aussi la page <RouterLink to="/securite">Sécurité</RouterLink>.
      </p>
    </div>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
