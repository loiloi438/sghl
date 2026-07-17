<template>
  <section class="pub-section">
    <p class="pub-eyebrow">Blog</p>
    <h1 class="pub-section-title">Conseils santé</h1>
    <p class="pub-section-sub">
      Articles simples pour la prévention et le bien-être. Lecture libre en mode observateur.
    </p>

    <div class="pub-grid pub-grid-3">
      <RouterLink
        v-for="post in blogPosts"
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
        <p style="font-size: 0.8rem; color: #64748b; margin: 0 1.35rem 1.25rem">
          {{ post.readMinutes }} min de lecture
        </p>
      </RouterLink>
    </div>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { blogPosts } from '../../data/publicContent.js'
</script>
