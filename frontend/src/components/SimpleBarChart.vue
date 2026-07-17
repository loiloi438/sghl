<template>
  <div class="chart" role="img" :aria-label="ariaLabel">
    <div class="chart-bars">
      <div v-for="(point, index) in series" :key="index" class="chart-col">
        <div
          class="chart-bar"
          :style="{
            height: barHeight(point.value),
            background: point.color
              ? `linear-gradient(180deg, ${point.color} 0%, ${point.color}99 100%)`
              : undefined,
          }"
          :title="`${point.label}: ${formatValue(point.value)}`"
        />
        <span class="chart-label">{{ point.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  series: { type: Array, default: () => [] },
  ariaLabel: { type: String, default: 'Graphique en barres' },
})

const maxValue = computed(() => {
  const values = props.series.map((p) => p.value)
  return Math.max(...values, 1)
})

function barHeight(value) {
  const pct = Math.round((value / maxValue.value) * 100)
  return `${Math.max(pct, 4)}%`
}

function formatValue(value) {
  const n = Number(value)
  if (!Number.isFinite(n)) return value
  if (n >= 1000) return `${Math.round(n).toLocaleString('fr-FR')}`
  return String(n)
}
</script>

<style scoped>
.chart {
  padding: 0.5rem 0 0;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  height: 140px;
}

.chart-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  min-width: 0;
}

.chart-bar {
  width: 100%;
  max-width: 2.5rem;
  margin-top: auto;
  border-radius: 6px 6px 2px 2px;
  background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-accent) 100%);
  transition: height 0.35s ease;
}

.chart-label {
  margin-top: 0.45rem;
  font-size: 0.65rem;
  color: var(--color-muted);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}
</style>
