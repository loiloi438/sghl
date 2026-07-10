<template>
  <svg
    class="nav-icon"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.75"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <component :is="iconComponent" />
  </svg>
</template>

<script setup>
import { computed, h } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
})

const icons = {
  dashboard: () => [
    h('rect', { x: '3', y: '3', width: '7', height: '7', rx: '1.5' }),
    h('rect', { x: '14', y: '3', width: '7', height: '7', rx: '1.5' }),
    h('rect', { x: '3', y: '14', width: '7', height: '7', rx: '1.5' }),
    h('rect', { x: '14', y: '14', width: '7', height: '7', rx: '1.5' }),
  ],
  patients: () => [
    h('path', { d: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2' }),
    h('circle', { cx: '9', cy: '7', r: '4' }),
    h('path', { d: 'M22 21v-2a4 4 0 0 0-3-3.87' }),
    h('path', { d: 'M16 3.13a4 4 0 0 1 0 7.75' }),
  ],
  calendar: () => [
    h('rect', { x: '3', y: '4', width: '18', height: '18', rx: '2' }),
    h('path', { d: 'M16 2v4M8 2v4M3 10h18' }),
    h('path', { d: 'M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01' }),
  ],
  prescription: () => [
    h('path', { d: 'M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z' }),
    h('path', { d: 'M12 8v8M8 12h8' }),
  ],
  lab: () => [
    h('path', { d: 'M9 3h6l3 7-6 11-6-11 3-7z' }),
    h('path', { d: 'M6 10h12' }),
  ],
  billing: () => [
    h('path', { d: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z' }),
    h('path', { d: 'M14 2v6h6M16 13H8M16 17H8M10 9H8' }),
  ],
  hospital: () => [
    h('path', { d: 'M3 21h18M5 21V7l7-4 7 4v14' }),
    h('path', { d: 'M12 11v4M10 13h4' }),
  ],
  care: () => [
    h('path', { d: 'M12 21s-7-4.5-7-10a4 4 0 0 1 7-2 7 2a4 4 0 0 1-7 10z' }),
  ],
  pharmacy: () => [
    h('path', { d: 'm10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7z' }),
    h('path', { d: 'm8.5 8.5 7 7' }),
  ],
  location: () => [
    h('path', { d: 'M12 21s-6-4.35-6-10a6 6 0 1 1 12 0c0 5.65-6 10-6 10z' }),
    h('circle', { cx: '12', cy: '10', r: '2.5' }),
  ],
}

const iconComponent = computed(() => {
  const render = icons[props.name] || icons.dashboard
  return { render: () => h('g', {}, render()) }
})
</script>

<style scoped>
.nav-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.nav-icon:hover {
  filter: drop-shadow(0 6px 14px rgba(37, 99, 235, 0.08));
}
</style>
