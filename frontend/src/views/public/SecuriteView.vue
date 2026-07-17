<template>
  <div>
    <section class="pub-section">
      <p class="pub-eyebrow">Confiance</p>
      <h1 class="pub-section-title">Sécurité & protection des données</h1>
      <p class="pub-section-sub">
        Votre santé mérite la plus grande confidentialité. SGHL combine chiffrement,
        contrôle d’accès et conformité RGPD.
      </p>

      <div class="pub-grid pub-grid-2">
        <article v-for="p in securityPoints" :key="p.title" class="pub-card">
          <div class="pub-icon" aria-hidden="true">🔒</div>
          <h3>{{ p.title }}</h3>
          <p>{{ p.text }}</p>
        </article>
      </div>

      <div class="pub-card pub-card--split" style="margin-top: 1.5rem">
        <div>
          <h3>Paiement sécurisé</h3>
          <p>
            Les règlements de factures passent par des canaux protégés (paiement mobile et carte).
            SGHL ne conserve pas vos numéros de carte en clair.
          </p>
          <div class="pub-payment-row">
            <span class="pub-pay-badge">📱 MTN / Orange Money</span>
            <span class="pub-pay-badge">💳 Carte</span>
            <span class="pub-pay-badge">🛡️ HTTPS</span>
          </div>
        </div>
        <img
          class="pub-side-photo"
          src="/images/visitor/secure.jpg"
          alt="Illustration sécurité des paiements et données"
          width="320"
          height="220"
          loading="lazy"
        />
      </div>
    </section>

    <section class="pub-section">
      <VisitorGateCta
        title="Prêt à accéder à votre espace sécurisé ?"
        message="Pour continuer et accéder à vos informations personnelles, veuillez vous connecter 💙"
        redirect="/patient"
      />
    </section>
  </div>
</template>

<script setup>
import VisitorGateCta from '../../components/public/VisitorGateCta.vue'
import { securityPoints } from '../../data/publicContent.js'
</script>
