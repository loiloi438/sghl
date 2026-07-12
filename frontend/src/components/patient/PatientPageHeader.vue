<template>
  <header class="hc-page-header">
    <div class="hc-page-header-body">
      <p v-if="showTag" class="hc-hero-tag hc-page-tag">🌿 Human-Care</p>
      <h1 class="hc-page-title">{{ title }}</h1>
      <p v-if="subtitle" class="hc-page-sub">{{ subtitle }}</p>
    </div>
    <PatientModuleIllustration v-if="module" :variant="module" class="hc-page-header-art" />
    <button
      type="button"
      class="hc-btn-secondary hc-page-header-refresh"
      :disabled="loading"
      @click="$emit('refresh')"
    >
      {{ loading ? 'Actualisation…' : '↻ Actualiser' }}
    </button>
  </header>
</template>

<script setup>
import PatientModuleIllustration from './PatientModuleIllustration.vue'

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  module: { type: String, default: '' },
  showTag: { type: Boolean, default: true },
})

defineEmits(['refresh'])
</script>
