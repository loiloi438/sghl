<template>
  <div class="visitor-gate">
    <div>
      <p class="pub-eyebrow">Espace personnel</p>
      <h2>{{ title }}</h2>
      <p>{{ resolvedMessage }}</p>
      <div class="visitor-gate-actions">
        <RouterLink
          class="btn-public-primary"
          :to="{ name: 'login', query: loginQuery }"
        >
          {{ t('nav.login') }} →
        </RouterLink>
        <RouterLink
          class="btn-public-secondary"
          :to="{ name: 'login', query: { ...loginQuery, mode: 'register' } }"
        >
          {{ t('nav.register') }}
        </RouterLink>
      </div>
    </div>
    <img
      class="visitor-gate-photo"
      src="/images/visitor/secure.jpg"
      alt="Accès sécurisé à vos informations de santé"
      width="420"
      height="280"
      loading="lazy"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from '../../composables/useI18n.js'

const props = defineProps({
  title: {
    type: String,
    default: 'Pour accéder à vos informations personnelles',
  },
  message: {
    type: String,
    default: '',
  },
  redirect: {
    type: String,
    default: '/patient',
  },
})

const { t } = useI18n()

const resolvedMessage = computed(() => props.message || t('cta.continue'))

const loginQuery = computed(() => ({
  reason: 'personal',
  redirect: props.redirect,
}))
</script>
