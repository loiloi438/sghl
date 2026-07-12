<template>
  <div class="hc-empty">
    <div class="hc-empty-icon">{{ icon }}</div>
    <p class="hc-empty-title">{{ title }}</p>
    <p v-if="text" class="hc-empty-text">{{ text }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '💙' },
  title: { type: String, required: true },
  text: { type: String, default: '' },
})
</script>
