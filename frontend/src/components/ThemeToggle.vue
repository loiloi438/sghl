<template>
  <button
    type="button"
    class="theme-toggle"
    aria-label="Thème clair SGHL"
    title="Interface en mode clair harmonisé"
    @click="toggleTheme"
  >
    <span class="theme-icon" aria-hidden="true">☀️</span>
    <span class="theme-label">Clair</span>
  </button>
</template>

<script setup>
import { useTheme } from '../composables/useTheme.js'

const { theme, toggleTheme } = useTheme()
</script>

<style scoped>
.theme-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    background var(--transition-fast),
    border-color var(--transition-fast),
    color var(--transition-fast);
}

.theme-toggle:hover {
  border-color: var(--color-primary);
  color: var(--color-text);
  background: var(--color-primary-light);
}

.theme-icon {
  font-size: 0.95rem;
  line-height: 1;
}

.theme-label {
  display: none;
}

@media (min-width: 640px) {
  .theme-label {
    display: inline;
  }
}
</style>
