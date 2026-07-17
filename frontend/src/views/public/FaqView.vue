<template>
  <section class="pub-section pub-faq">
    <p class="pub-eyebrow">Aide</p>
    <h1 class="pub-section-title">Foire aux questions</h1>
    <p class="pub-section-sub">
      Cliquez sur une question pour afficher la réponse. Aucune connexion n’est requise.
    </p>

    <details v-for="(item, i) in faqItems" :key="i">
      <summary>{{ item.q }}</summary>
      <p>{{ item.a }}</p>
    </details>

    <div style="margin-top: 2rem">
      <VisitorGateCta redirect="/patient" />
    </div>
  </section>
</template>

<script setup>
import VisitorGateCta from '../../components/public/VisitorGateCta.vue'
import { faqItems } from '../../data/publicContent.js'
</script>
