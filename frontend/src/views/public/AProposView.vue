<template>
  <section class="pub-section pub-legal">
    <p class="pub-eyebrow">SGHL</p>
    <h1 class="pub-section-title">À propos de SGHL</h1>
    <p class="pub-section-sub">
      Système de Gestion Hospitalière — une plateforme Human-Care pour patients et personnel,
      pensée pour rassurer, simplifier et sécuriser le parcours de soins.
    </p>

    <div class="pub-about-hero">
      <img
        src="/images/visitor/infra.jpg"
        alt="Établissement SGHL"
        width="960"
        height="420"
        loading="eager"
      />
    </div>

    <div class="pub-grid pub-grid-3" style="margin-top: 1.5rem">
      <article class="pub-card">
        <div class="pub-icon" aria-hidden="true">🎯</div>
        <h3>Mission</h3>
        <p>
          Faciliter l’accès aux soins : rendez-vous, résultats, factures et suivi, dans une
          interface claire et bienveillante.
        </p>
      </article>
      <article class="pub-card">
        <div class="pub-icon" aria-hidden="true">🔭</div>
        <h3>Vision</h3>
        <p>
          Un hôpital numérique de confiance, où chaque rôle (patient, secrétaire, médecin, admin)
          dispose d’un espace adapté et sécurisé.
        </p>
      </article>
      <article class="pub-card">
        <div class="pub-icon" aria-hidden="true">💙</div>
        <h3>Valeurs</h3>
        <p>
          Empathie, confidentialité, disponibilité 24/7 et excellence opérationnelle — Human-Care
          pour les patients, Tech-Health pour le personnel.
        </p>
      </article>
    </div>

    <div class="pub-card" style="margin-top: 1.5rem">
      <h3>Ce que SGHL propose</h3>
      <p>
        Une vitrine publique (mode observateur), un portail patient, et un ERP staff pour la
        gestion des rendez-vous, du laboratoire, de la pharmacie, de la facturation et plus encore.
      </p>
      <div class="pub-hero-actions" style="margin-top: 1rem">
        <RouterLink class="btn-public-primary" to="/nos-services">Nos services</RouterLink>
        <RouterLink class="btn-public-secondary" to="/presentation">Présentation</RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
