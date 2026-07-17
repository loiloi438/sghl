<template>
  <article v-if="post" class="pub-article">
    <RouterLink to="/blog" class="btn-public-secondary" style="display: inline-flex; margin-bottom: 1rem">
      ← Conseils santé
    </RouterLink>
    <img
      v-if="post.image"
      :src="post.image"
      :alt="post.title"
      class="pub-article-cover"
      width="720"
      height="360"
      loading="eager"
    />
    <span class="pub-tag">{{ post.tag }}</span>
    <h1>{{ post.title }}</h1>
    <p class="meta">{{ post.readMinutes }} min de lecture · Contenu informatif — ne remplace pas une consultation</p>
    <p v-for="(para, i) in post.body" :key="i">{{ para }}</p>

    <div style="margin-top: 2.5rem">
      <VisitorGateCta
        title="Besoin d’un suivi personnalisé ?"
        message="Pour continuer et accéder à vos informations personnelles, veuillez vous connecter 💙"
        redirect="/patient/rendez-vous"
      />
    </div>
  </article>

  <section v-else class="pub-section">
    <h1 class="pub-section-title">Article introuvable</h1>
    <p class="pub-section-sub">Ce conseil santé n’existe pas ou a été déplacé.</p>
    <RouterLink class="btn-public-primary" to="/blog">Retour au blog</RouterLink>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import VisitorGateCta from '../../components/public/VisitorGateCta.vue'
import { getBlogPost } from '../../data/publicContent.js'

const route = useRoute()
const post = computed(() => getBlogPost(String(route.params.slug || '')))
</script>
