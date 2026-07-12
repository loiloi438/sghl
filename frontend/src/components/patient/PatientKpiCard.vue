<template>
  <article class="hc-kpi" :class="`hc-kpi--${tone}`">
    <span class="hc-kpi-label" :style="{ color: labelColor }">{{ label }}</span>
    <p class="hc-kpi-value">{{ value }}</p>
    <p v-if="detail" class="hc-kpi-detail">{{ detail }}</p>
  </article>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  detail: { type: String, default: '' },
  tone: { type: String, default: 'mint' },
  labelColor: { type: String, default: '#0d9488' },
})
</script>
