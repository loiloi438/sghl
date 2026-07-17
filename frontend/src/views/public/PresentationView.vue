<template>
  <div>
    <section class="pub-presentation-hero">
      <img
        class="pub-presentation-cover"
        src="/images/visitor/infra.jpg"
        alt="Infrastructure moderne du CHU SGHL"
        width="1400"
        height="520"
        loading="eager"
      />
      <div class="pub-presentation-overlay">
        <p class="pub-eyebrow" style="color: #ccfbf1">Présentation</p>
        <h1>Un établissement moderne, une équipe à votre écoute</h1>
        <p>
          Infrastructure soignée, laboratoire certifié et accompagnement Human-Care — pour des
          soins clairs, accessibles et rassurants.
        </p>
      </div>
    </section>

    <section class="pub-section">
      <div class="pub-grid pub-grid-3">
        <article v-for="card in highlightCards" :key="card.title" class="pub-card pub-card--photo">
          <div class="pub-card-media">
            <img :src="card.image" :alt="card.title" width="480" height="320" loading="lazy" />
          </div>
          <h3>{{ card.title }}</h3>
          <p>{{ card.text }}</p>
        </article>
      </div>
    </section>

    <section class="pub-section">
      <h2 class="pub-section-title">{{ t('engagements.title') }}</h2>
      <p class="pub-section-sub">{{ t('engagements.sub') }}</p>
      <div class="pub-grid pub-grid-3">
        <article v-for="item in engagements" :key="item.title" class="pub-card">
          <div class="pub-icon" aria-hidden="true">{{ item.icon }}</div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.text }}</p>
        </article>
      </div>
    </section>

    <section class="pub-section">
      <VisitorGateCta redirect="/patient" />
    </section>
  </div>
</template>

<script setup>
import VisitorGateCta from '../../components/public/VisitorGateCta.vue'
import { useI18n } from '../../composables/useI18n.js'
import { highlightCards } from '../../data/publicContent.js'

const { t } = useI18n()

const engagements = [
  {
    icon: '🔒',
    title: 'Sécurité',
    text: 'Connexion chiffrée, contrôle des rôles et protection des accès sensibles.',
  },
  {
    icon: '🛡️',
    title: 'Confidentialité',
    text: 'Vos données de santé restent privées — conformité RGPD et consentement explicite.',
  },
  {
    icon: '🕒',
    title: 'Disponibilité 24/7',
    text: 'Votre espace patient reste accessible jour et nuit, où que vous soyez.',
  },
]
</script>
