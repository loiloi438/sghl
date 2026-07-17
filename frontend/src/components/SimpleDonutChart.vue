<template>
  <div class="donut" role="img" :aria-label="ariaLabel">
    <svg viewBox="0 0 42 42" class="donut-svg">
      <circle class="donut-track" cx="21" cy="21" r="15.915" />
      <circle
        v-for="(seg, index) in segments"
        :key="index"
        class="donut-segment"
        cx="21"
        cy="21"
        r="15.915"
        :stroke="seg.color"
        :stroke-dasharray="seg.dash"
        :stroke-dashoffset="seg.offset"
      />
      <text x="21" y="20.5" class="donut-total">{{ total }}</text>
      <text x="21" y="25.5" class="donut-caption">total</text>
    </svg>
    <ul class="donut-legend">
      <li v-for="(item, index) in series" :key="index">
        <span class="swatch" :style="{ background: item.color || colors[index % colors.length] }" />
        <span class="label">{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  series: { type: Array, default: () => [] },
  ariaLabel: { type: String, default: 'Graphique en anneau' },
})

const colors = ['#38bdf8', '#34d399', '#a78bfa', '#fbbf24', '#f97316']

const total = computed(() =>
  props.series.reduce((sum, item) => sum + Number(item.value || 0), 0),
)

const segments = computed(() => {
  const sum = total.value || 1
  let cursor = 25
  return props.series.map((item, index) => {
    const value = Number(item.value || 0)
    const pct = (value / sum) * 100
    const seg = {
      color: item.color || colors[index % colors.length],
      dash: `${pct} ${100 - pct}`,
      offset: cursor,
    }
    cursor -= pct
    return seg
  })
})
</script>

<style scoped>
.donut {
  display: grid;
  gap: 1rem;
  align-items: center;
}

@media (min-width: 420px) {
  .donut {
    grid-template-columns: 140px 1fr;
  }
}

.donut-svg {
  width: 140px;
  height: 140px;
  transform: rotate(-90deg);
}

.donut-track {
  fill: transparent;
  stroke: rgba(148, 163, 184, 0.2);
  stroke-width: 4;
}

.donut-segment {
  fill: transparent;
  stroke-width: 4;
  stroke-linecap: round;
  transition: stroke-dasharray 0.4s ease;
}

.donut-total,
.donut-caption {
  transform: rotate(90deg);
  transform-origin: 21px 21px;
  text-anchor: middle;
  fill: #e2e8f0;
}

.donut-total {
  font-size: 0.45rem;
  font-weight: 700;
}

.donut-caption {
  font-size: 0.22rem;
  fill: #94a3b8;
}

.donut-legend {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.55rem;
}

.donut-legend li {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.5rem;
  align-items: center;
  font-size: 0.8rem;
  color: #cbd5e1;
}

.swatch {
  width: 0.65rem;
  height: 0.65rem;
  border-radius: 999px;
}

.label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
