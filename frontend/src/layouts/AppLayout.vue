<template>
  <div class="layout" :class="{ 'layout--menu-open': menuOpen }">
    <button
      type="button"
      class="menu-toggle"
      aria-label="Menu"
      :aria-expanded="menuOpen"
      @click="menuOpen = !menuOpen"
    >
      <span />
      <span />
      <span />
    </button>

    <div v-if="menuOpen" class="sidebar-backdrop" @click="menuOpen = false" />

    <aside class="sidebar">
      <div class="brand">
        <div class="brand-icon">+</div>
        <div>
          <span class="brand-mark">SGHL</span>
          <span class="brand-sub">Centre hospitalier</span>
        </div>
      </div>

      <SidebarNav :navigation="navigation" @navigate="menuOpen = false" />

      <div class="sidebar-footer">
        <RouterLink to="/profil" class="user-card user-card--link" @click="menuOpen = false">
          <div class="user-avatar">{{ initials }}</div>
          <div>
            <strong>{{ auth.fullName }}</strong>
            <span class="role">{{ roleLabel }}</span>
          </div>
        </RouterLink>
        <button class="btn btn-ghost logout" type="button" @click="logout">Déconnexion</button>
      </div>
    </aside>

    <div class="main-shell">
      <header class="topbar">
        <div class="topbar-left">
          <p class="topbar-breadcrumb">SGHL · Staff</p>
          <h1 class="topbar-title">{{ pageTitle }}</h1>
        </div>
        <div class="topbar-actions">
          <ThemeToggle />
          <span v-if="isPlaceholderRoute" class="placeholder-pill">Module en développement</span>
          <span v-if="roleLabel" class="role-pill">{{ roleLabel }}</span>
          <div class="topbar-meta">
            <span class="status-dot" />
            Système opérationnel
          </div>
        </div>
      </header>
      <main class="content">
        <RouterView v-slot="{ Component }">
          <Transition name="page-fade" mode="out-in">
            <component :is="Component" :key="route.path" />
          </Transition>
        </RouterView>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, Transition, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import SidebarNav from '../components/SidebarNav.vue'
import ThemeToggle from '../components/ThemeToggle.vue'
import { useNavigation } from '../composables/useNavigation.js'
import { isPlaceholderRoute as isRegisteredPlaceholder } from '../config/navigation.js'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const { navigation } = useNavigation()
const router = useRouter()
const route = useRoute()
const menuOpen = ref(false)

const roleLabels = {
  admin: 'Administrateur',
  medecin: 'Médecin',
  infirmier: 'Infirmier(ère)',
  biologiste: 'Biologiste',
  pharmacien: 'Pharmacien',
  comptable: 'Comptable',
}

const roleLabel = computed(() => roleLabels[auth.role] || auth.role)
const pageTitle = computed(() => route.meta.title || 'Tableau de bord')
const isPlaceholderRoute = computed(
  () => route.meta.placeholder || isRegisteredPlaceholder(route.name),
)
const initials = computed(() => {
  const name = auth.fullName || auth.user?.username || 'U'
  return name
    .split(/\s+/)
    .map((p) => p[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
})

watch(
  () => route.path,
  () => {
    menuOpen.value = false
  },
)

async function logout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
}

.menu-toggle {
  display: none;
  position: fixed;
  top: 0.85rem;
  left: 0.85rem;
  z-index: 50;
  width: 2.5rem;
  height: 2.5rem;
  padding: 0.45rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  box-shadow: var(--shadow-sm);
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  cursor: pointer;
}

.menu-toggle span {
  display: block;
  height: 2px;
  background: var(--color-text);
  border-radius: 1px;
}

.sidebar-backdrop {
  display: none;
}

.sidebar {
  width: var(--sidebar-width);
  background: linear-gradient(180deg, var(--color-surface) 0%, var(--color-bg) 100%);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: 1.35rem 0.9rem;
  flex-shrink: 0;
  z-index: 40;
  box-shadow: 4px 0 24px rgba(15, 23, 42, 0.03);
  overflow: hidden;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 0.5rem 1.25rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.brand-icon {
  width: 2.35rem;
  height: 2.35rem;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  color: white;
  display: grid;
  place-items: center;
  font-size: 1.35rem;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
}

.brand-mark {
  display: block;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: 0.04em;
}

.brand-sub {
  font-size: 0.75rem;
  color: var(--color-muted);
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 0.75rem;
}

.user-card--link {
  text-decoration: none;
  color: inherit;
  border-radius: 0.75rem;
  padding: 0.35rem;
  margin: -0.35rem -0.35rem 0.4rem;
  transition: background 0.15s ease;
}

.user-card--link:hover {
  background: var(--color-surface-muted, rgba(148, 163, 184, 0.12));
}

.user-avatar {
  width: 2.35rem;
  height: 2.35rem;
  border-radius: 999px;
  background: linear-gradient(145deg, var(--color-primary) 0%, var(--color-accent) 100%);
  color: white;
  font-size: 0.72rem;
  font-weight: 800;
  display: grid;
  place-items: center;
  box-shadow: 0 2px 10px rgba(37, 99, 235, 0.25);
}

.user-card strong {
  display: block;
  font-size: 0.875rem;
}

.role {
  font-size: 0.75rem;
  color: var(--color-muted);
}

.logout {
  width: 100%;
}

.main-shell {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.85rem;
  padding: 0.9rem clamp(1rem, 3vw, 2rem);
  background: color-mix(in srgb, var(--color-surface) 90%, transparent);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border-soft);
  position: sticky;
  top: 0;
  z-index: 10;
}

.topbar-left {
  min-width: 0;
}

.topbar-breadcrumb {
  margin: 0;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-muted);
}

.topbar-title {
  margin: 0.15rem 0 0;
  font-size: clamp(1.15rem, 2.5vw, 1.35rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--color-text);
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.role-pill {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  border: 1px solid rgba(37, 99, 235, 0.15);
}

.placeholder-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: var(--color-warning-light);
  color: var(--color-warning);
  border: 1px solid rgba(251, 191, 36, 0.35);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.topbar-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-accent-dark);
  padding: 0.4rem 0.85rem;
  background: linear-gradient(135deg, var(--color-accent-light) 0%, #f0fdf9 100%);
  border-radius: 999px;
  border: 1px solid #a7f3d0;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--color-success);
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.2);
}

.content {
  flex: 1;
  padding: clamp(1rem, 3vw, 1.5rem) clamp(1rem, 3vw, 2rem) 2rem;
  overflow-x: hidden;
}

.content :deep(.page-header > h1) {
  display: none;
}

@media (max-width: 900px) {
  .menu-toggle {
    display: flex;
  }

  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.4);
    z-index: 35;
  }

  .layout:not(.layout--menu-open) .sidebar-backdrop {
    display: none;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
    box-shadow: var(--shadow-lg);
  }

  .layout--menu-open .sidebar {
    transform: translateX(0);
  }

  .main-shell {
    width: 100%;
  }

  .topbar {
    padding-left: 3.5rem;
  }
}
</style>
