<template>
  <div class="line-chart" role="img" :aria-label="ariaLabel">
    <svg :viewBox="`0 0 ${width} ${height}`" class="line-svg" preserveAspectRatio="none">
      <g v-for="(serie, sIndex) in paths" :key="sIndex">
        <polyline
          fill="none"
          :stroke="serie.color"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          :points="serie.points"
        />
        <circle
          v-for="(pt, pIndex) in serie.dots"
          :key="`${sIndex}-${pIndex}`"
          :cx="pt.x"
          :cy="pt.y"
          r="3"
          :fill="serie.color"
        />
      </g>
    </svg>
    <div class="line-labels">
      <span v-for="(label, index) in labels" :key="index">{{ label }}</span>
    </div>
    <ul class="line-legend">
      <li v-for="(serie, index) in series" :key="index">
        <span class="swatch" :style="{ background: serie.color }" />
        {{ serie.label }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  labels: { type: Array, default: () => [] },
  series: { type: Array, default: () => [] },
  ariaLabel: { type: String, default: 'Graphique linéaire' },
})

const width = 320
const height = 140
const padX = 8
const padY = 12

const paths = computed(() => {
  const allValues = props.series.flatMap((s) => s.values || [])
  const max = Math.max(...allValues, 1)
  const count = Math.max(props.labels.length - 1, 1)

  return props.series.map((serie) => {
    const values = serie.values || []
    const dots = values.map((value, index) => {
      const x = padX + (index / count) * (width - padX * 2)
      const y = height - padY - (Number(value) / max) * (height - padY * 2)
      return { x, y }
    })
    return {
      color: serie.color || '#38bdf8',
      points: dots.map((d) => `${d.x},${d.y}`).join(' '),
      dots,
    }
  })
})
</script>

<style scoped>
.line-chart {
  display: grid;
  gap: 0.65rem;
}

.line-svg {
  width: 100%;
  height: 140px;
}

.line-labels {
  display: flex;
  justify-content: space-between;
  gap: 0.25rem;
  font-size: 0.65rem;
  color: #64748b;
}

.line-legend {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: #cbd5e1;
}

.line-legend li {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.swatch {
  width: 0.55rem;
  height: 0.55rem;
  border-radius: 999px;
}
</style>
