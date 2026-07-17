<template>
  <div>
    <section class="pub-section pub-hero">
      <div>
        <p class="pub-eyebrow">Mode observateur</p>
        <h1>{{ t('hero.title') }}</h1>
        <p class="lead">{{ t('hero.lead') }}</p>
        <div class="pub-hero-actions">
          <RouterLink class="btn-public-primary" :to="{ name: 'login' }">{{ t('nav.login') }}</RouterLink>
          <RouterLink
            class="btn-public-secondary"
            :to="{ name: 'login', query: { mode: 'register' } }"
          >
            {{ t('nav.register') }}
          </RouterLink>
          <RouterLink class="btn-public-secondary" to="/nos-services">{{ t('nav.services') }}</RouterLink>
        </div>
      </div>

      <div class="pub-hero-visual">
        <img
          class="pub-hero-photo"
          src="/images/visitor/hero-family.jpg"
          alt="Famille accueillie devant le centre hospitalier SGHL"
          width="640"
          height="480"
          loading="eager"
        />
        <div class="pub-hero-badges" aria-label="Points forts de l’établissement">
          <figure
            v-for="card in highlightCards"
            :key="card.title"
            class="pub-hero-badge"
          >
            <img :src="card.image" :alt="card.title" width="120" height="120" loading="lazy" />
            <figcaption>{{ card.title }}</figcaption>
          </figure>
        </div>
      </div>
    </section>

    <section id="presentation" class="pub-section">
      <h2 class="pub-section-title">Présentation de l’établissement</h2>
      <p class="pub-section-sub">
        Infrastructure moderne, équipe soignante et laboratoire — un parcours clair et rassurant.
      </p>
      <div class="pub-grid pub-grid-3">
        <article v-for="card in highlightCards" :key="card.title" class="pub-card pub-card--photo">
          <div class="pub-card-media">
            <img :src="card.image" :alt="card.title" width="480" height="320" loading="lazy" />
          </div>
          <h3>{{ card.title }}</h3>
          <p>{{ card.text }}</p>
        </article>
      </div>
      <div class="pub-hero-actions" style="margin-top: 1.25rem">
        <RouterLink class="btn-public-secondary" to="/presentation">Découvrir la présentation</RouterLink>
        <RouterLink class="btn-public-secondary" to="/a-propos">À propos de SGHL</RouterLink>
      </div>
    </section>

    <section id="engagements" class="pub-section">
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
      <h2 class="pub-section-title">Nos services</h2>
      <p class="pub-section-sub">Des services pensés pour rassurer — accessibles 24h/24 depuis votre espace patient.</p>
      <div class="pub-grid pub-grid-services">
        <article v-for="s in previewServices" :key="s.id" class="pub-card">
          <div class="pub-icon" aria-hidden="true">{{ iconFor(s.icon) }}</div>
          <h3>{{ s.title }}</h3>
          <p>{{ s.text }}</p>
          <button type="button" class="btn-public-primary" style="margin-top: 1rem" @click="gateTo(s.redirect)">
            {{ s.cta }}
          </button>
        </article>
      </div>
      <div class="pub-card pub-card--split" style="margin-top: 1.25rem">
        <div>
          <h3>Paiement simplifié</h3>
          <p>Réglez vos factures depuis le portail patient, en toute sécurité.</p>
          <div class="pub-payment-row">
            <span class="pub-pay-badge">📱 Paiement mobile</span>
            <span class="pub-pay-badge">🟠 MTN · Orange</span>
            <span class="pub-pay-badge">💳 Carte bancaire</span>
          </div>
        </div>
        <img
          class="pub-side-photo"
          src="/images/visitor/secure.jpg"
          alt="Paiement et données de santé sécurisés"
          width="320"
          height="220"
          loading="lazy"
        />
      </div>
    </section>

    <section class="pub-section pub-section--tight">
      <div class="pub-grid pub-grid-2">
        <article class="pub-card pub-card--photo">
          <div class="pub-card-media pub-card-media--short">
            <img
              src="/images/visitor/equipe.jpg"
              alt="Équipe soignante SGHL"
              width="480"
              height="240"
              loading="lazy"
            />
          </div>
          <p class="pub-eyebrow">FAQ</p>
          <h3>Réponses à vos questions</h3>
          <p>Inscription, rendez-vous, résultats, paiements… tout est expliqué simplement.</p>
          <RouterLink class="btn-public-secondary" to="/faq" style="margin-top: 1rem; display: inline-flex">
            Ouvrir la FAQ
          </RouterLink>
        </article>
        <article class="pub-card">
          <p class="pub-eyebrow">Témoignage</p>
          <blockquote class="pub-quote">« {{ featuredQuote.quote }} »</blockquote>
          <div class="pub-quote-meta">
            <img
              class="pub-avatar pub-avatar--img"
              src="/images/visitor/equipe.jpg"
              :alt="`Portrait anonymisé ${featuredQuote.initials}`"
              width="40"
              height="40"
              loading="lazy"
            />
            <span>
              <strong>{{ featuredQuote.initials }}</strong>
              · {{ featuredQuote.role }}
            </span>
          </div>
        </article>
      </div>
    </section>

    <section class="pub-section">
      <h2 class="pub-section-title">Conseils santé</h2>
      <p class="pub-section-sub">Articles courts pour mieux prendre soin de vous — lecture libre, sans connexion.</p>
      <div class="pub-grid pub-grid-3">
        <RouterLink
          v-for="post in blogPreview"
          :key="post.slug"
          class="pub-card pub-blog-card pub-card--photo"
          :to="`/blog/${post.slug}`"
        >
          <div class="pub-card-media pub-card-media--blog">
            <img :src="post.image" :alt="post.title" width="480" height="270" loading="lazy" />
          </div>
          <span class="pub-tag">{{ post.tag }}</span>
          <h3>{{ post.title }}</h3>
          <p>{{ post.excerpt }}</p>
        </RouterLink>
      </div>
    </section>

    <section class="pub-section">
      <VisitorGateCta redirect="/patient" />
    </section>
  </div>
</template>

<script setup>
import { RouterLink, useRouter } from 'vue-router'
import VisitorGateCta from '../../components/public/VisitorGateCta.vue'
import { useI18n } from '../../composables/useI18n.js'
import {
  blogPosts,
  highlightCards,
  serviceCards,
  testimonials,
} from '../../data/publicContent.js'

const { t } = useI18n()
const router = useRouter()
const previewServices = serviceCards.slice(0, 4)
const blogPreview = blogPosts.slice(0, 3)
const featuredQuote = testimonials[0]

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

function iconFor(name) {
  const map = {
    building: '🏥',
    team: '👩‍⚕️',
    lab: '🔬',
    heart: '💙',
    pharmacy: '💊',
    care: '🩺',
    billing: '🧾',
    clock: '🕒',
  }
  return map[name] || '✨'
}

function gateTo(redirect) {
  router.push({
    name: 'login',
    query: { reason: 'personal', redirect },
  })
}
</script>
