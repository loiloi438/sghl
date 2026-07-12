<template>
  <nav class="sidebar-nav">
    <section
      v-for="section in navigation"
      :key="section.id"
      class="nav-section"
      :class="{ 'nav-section--clinical': section.id === 'clinical' }"
    >
      <button
        type="button"
        class="nav-section-toggle"
        :aria-expanded="!collapsed[section.id]"
        @click="toggleSection(section.id)"
      >
        <span class="nav-label">{{ section.label }}</span>
        <span class="nav-chevron" :class="{ 'nav-chevron--open': !collapsed[section.id] }">▸</span>
      </button>

      <div v-show="!collapsed[section.id]" class="nav-items">
        <template v-for="item in section.items" :key="item.to || item.id">
          <div v-if="item.children" class="nav-group">
            <span class="nav-group-label">
              <NavIcon :name="item.icon" />
              {{ item.label }}
            </span>
            <RouterLink
              v-for="child in item.children"
              :key="child.to"
              :to="child.to"
              class="nav-link nav-link--child"
              @click="emit('navigate')"
            >
              <NavIcon :name="child.icon" />
              <span>{{ child.label }}</span>
              <span
                v-if="child.to === '/notifications' && notificationCount > 0"
                class="nav-count-badge"
              >{{ notificationCount > 99 ? '99+' : notificationCount }}</span>
              <span v-if="child.placeholder" class="nav-badge">Bientôt</span>
            </RouterLink>
          </div>

          <RouterLink
            v-else
            :to="item.to"
            class="nav-link"
            @click="emit('navigate')"
          >
            <NavIcon :name="item.icon" />
            <span>{{ item.label }}</span>
            <span
              v-if="item.to === '/notifications' && notificationCount > 0"
              class="nav-count-badge"
            >{{ notificationCount > 99 ? '99+' : notificationCount }}</span>
            <span v-if="item.placeholder" class="nav-badge">Bientôt</span>
          </RouterLink>
        </template>
      </div>
    </section>
  </nav>
</template>

<script setup>
import { reactive } from 'vue'
import { RouterLink } from 'vue-router'
import NavIcon from './NavIcon.vue'

const props = defineProps({
  navigation: { type: Array, required: true },
  notificationCount: { type: Number, default: 0 },
})

const emit = defineEmits(['navigate'])

const collapsed = reactive({})

function toggleSection(id) {
  collapsed[id] = !collapsed[id]
}

for (const section of props.navigation) {
  if (collapsed[section.id] === undefined) {
    collapsed[section.id] = false
  }
}
</script>

<style scoped>
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.nav-section {
  margin-bottom: 0.35rem;
}

.nav-section--clinical {
  padding: 0.5rem 0;
  margin-bottom: 0.65rem;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

.nav-section-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.35rem 0.65rem;
  margin-bottom: 0.25rem;
  border: none;
  background: transparent;
  cursor: pointer;
  text-align: left;
}

.nav-label {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--color-muted);
}

.nav-chevron {
  font-size: 0.75rem;
  color: var(--color-muted);
  transition: transform 0.2s ease;
}

.nav-chevron--open {
  transform: rotate(90deg);
}

.nav-items {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  color: var(--color-text-secondary);
  text-decoration: none;
  padding: 0.58rem 0.7rem;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-weight: 500;
  transition:
    background var(--transition-fast),
    color var(--transition-fast);
}

.nav-link--child {
  padding-left: 1.35rem;
  font-size: 0.85rem;
}

.nav-link.router-link-active {
  background: linear-gradient(90deg, rgba(37, 99, 235, 0.1) 0%, rgba(5, 150, 105, 0.06) 100%);
  color: var(--color-primary-dark);
  font-weight: 600;
  box-shadow: inset 3px 0 0 var(--color-primary);
}

.nav-link.router-link-active :deep(.nav-icon) {
  color: var(--color-primary);
}

.nav-link:hover:not(.router-link-active) {
  background: rgba(15, 23, 42, 0.04);
  color: var(--color-text);
}

.nav-group {
  display: flex;
  flex-direction: column;
  gap: 0.08rem;
  margin-bottom: 0.15rem;
}

.nav-group-label {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.45rem 0.7rem 0.25rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-muted);
}

.nav-badge {
  margin-left: auto;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.12rem 0.4rem;
  border-radius: 999px;
  background: var(--color-warning-light);
  color: var(--color-warning);
  border: 1px solid rgba(251, 191, 36, 0.35);
}

.nav-count-badge {
  margin-left: auto;
  min-width: 1.4rem;
  height: 1.4rem;
  padding: 0 0.35rem;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--color-danger, #dc2626);
  color: white;
  font-size: 0.68rem;
  font-weight: 800;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.25);
}
</style>
