<template>
  <section class="pub-section">
    <p class="pub-eyebrow">Confiance</p>
    <h1 class="pub-section-title">Témoignages patients</h1>
    <p class="pub-section-sub">
      Retours anonymisés de personnes ayant utilisé le portail SGHL. Les initiales protègent
      l’identité de chacun.
    </p>

    <div class="pub-grid pub-grid-2">
      <article v-for="t in testimonials" :key="t.id" class="pub-card">
        <blockquote class="pub-quote">« {{ t.quote }} »</blockquote>
        <div class="pub-quote-meta">
          <img
            class="pub-avatar pub-avatar--img"
            :src="t.id % 2 === 0 ? '/images/visitor/labo.jpg' : '/images/visitor/equipe.jpg'"
            :alt="`Portrait anonymisé ${t.initials}`"
            width="40"
            height="40"
            loading="lazy"
          />
          <span>
            <strong>{{ t.initials }}</strong>
            · {{ t.role }}
          </span>
        </div>
      </article>
    </div>

    <div style="margin-top: 2rem">
      <VisitorGateCta
        message="Pour continuer et accéder à vos informations personnelles, veuillez vous connecter 💙"
        redirect="/patient"
      />
    </div>
  </section>
</template>

<script setup>
import VisitorGateCta from '../../components/public/VisitorGateCta.vue'
import { testimonials } from '../../data/publicContent.js'
</script>
