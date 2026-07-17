<template>
  <div>
    <section class="pub-section">
      <p class="pub-eyebrow">Services</p>
      <h1 class="pub-section-title">Nos services hospitaliers</h1>
      <p class="pub-section-sub">
        Explorez librement ce que propose SGHL. Pour accéder à vos données personnelles
        (rendez-vous, ordonnances, factures…), une connexion patient est requise.
      </p>

      <div class="pub-grid pub-grid-3" style="margin-bottom: 1.5rem">
        <figure v-for="shot in showcase" :key="shot.title" class="pub-card pub-card--photo" style="margin: 0">
          <div class="pub-card-media">
            <img :src="shot.image" :alt="shot.title" width="480" height="320" loading="lazy" />
          </div>
          <h3>{{ shot.title }}</h3>
          <p>{{ shot.text }}</p>
        </figure>
      </div>

      <div class="pub-grid pub-grid-services">
        <article v-for="s in serviceCards" :key="s.id" class="pub-card">
          <div class="pub-icon" aria-hidden="true">{{ iconFor(s.icon) }}</div>
          <h3>{{ s.title }}</h3>
          <p>{{ s.text }}</p>
          <button type="button" class="btn-public-primary" style="margin-top: 1rem" @click="gateTo(s.redirect)">
            {{ s.cta }}
          </button>
        </article>
      </div>

      <div class="pub-grid pub-grid-3" style="margin-top: 1.5rem">
        <article v-for="f in trustFeatures" :key="f.title" class="pub-card">
          <div class="pub-icon" aria-hidden="true">{{ iconFor(f.icon) }}</div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.text }}</p>
        </article>
      </div>
    </section>

    <section class="pub-section">
      <VisitorGateCta redirect="/patient/rendez-vous" />
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import VisitorGateCta from '../../components/public/VisitorGateCta.vue'
import { highlightCards, serviceCards, trustFeatures } from '../../data/publicContent.js'

const router = useRouter()
const showcase = highlightCards

function iconFor(name) {
  const map = {
    heart: '💙',
    pharmacy: '💊',
    lab: '🔬',
    care: '🩺',
    billing: '🧾',
    clock: '🕒',
    pdf: '📄',
    mobile: '📱',
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
