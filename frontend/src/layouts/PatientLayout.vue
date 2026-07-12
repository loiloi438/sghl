<template>
  <div class="patient-layout patient-portal">
    <header class="patient-header">
      <div class="patient-header-inner">
        <RouterLink to="/patient" class="brand-link">
          <span class="brand-icon">+</span>
          <span>
            <strong>SGHL</strong>
            <small>Pour votre santé et bien-être</small>
          </span>
        </RouterLink>
        <button
          type="button"
          class="nav-toggle"
          :aria-expanded="navOpen"
          aria-controls="patient-nav"
          @click="navOpen = !navOpen"
        >
          {{ navOpen ? 'Fermer' : 'Menu' }}
        </button>
        <nav id="patient-nav" class="patient-nav" :class="{ 'patient-nav--open': navOpen }">
          <RouterLink
            v-for="link in patientNavLinks"
            :key="link.to"
            :to="link.to"
            custom
            v-slot="{ isActive, isExactActive, navigate }"
          >
            <a
              href="#"
              class="nav-pill"
              :class="(link.exact ? isExactActive : isActive) ? 'router-link-active' : ''"
              @click.prevent="navOpen = false; navigate()"
            >
              {{ link.label }}
              <span v-if="link.badge && unreadCount > 0" class="nav-badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
            </a>
          </RouterLink>
        </nav>
        <div class="patient-header-actions">
          <RouterLink to="/contact" class="btn btn-secondary btn-sm">Contact</RouterLink>
          <ThemeToggle />
          <span v-if="auth.user" class="user-name">{{ auth.fullName }}</span>
          <button type="button" class="btn btn-secondary btn-sm" @click="logout">Déconnexion</button>
        </div>
      </div>
    </header>
    <main class="patient-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import { patientNavLinks } from '../composables/usePatientPortal.js'
import { useAuthStore } from '../stores/auth.js'
import api from '../api/client.js'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const unreadCount = ref(0)
const navOpen = ref(false)

watch(() => route.path, () => {
  navOpen.value = false
})

async function loadUnread() {
  try {
    const { data } = await api.get('/patient/notifications/non-lues/')
    unreadCount.value = data.count ?? 0
  } catch {
    unreadCount.value = 0
  }
}

function onNotificationsUpdated(event) {
  if (event?.detail?.count != null) {
    unreadCount.value = event.detail.count
  } else {
    loadUnread()
  }
}

async function logout() {
  await auth.logout()
  router.push({ name: 'login' })
}

onMounted(() => {
  loadUnread()
  window.addEventListener('patient-notifications-updated', onNotificationsUpdated)
})

onUnmounted(() => {
  window.removeEventListener('patient-notifications-updated', onNotificationsUpdated)
})
</script>

<style scoped>
.patient-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

.patient-header {
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  position: sticky;
  top: 0;
  z-index: 20;
}

.patient-header-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0.75rem 1.25rem;
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-areas:
    'brand actions'
    'toggle toggle'
    'nav nav';
  align-items: center;
  gap: 0.75rem;
}

.brand-link {
  grid-area: brand;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: inherit;
}

.brand-link strong {
  display: block;
  font-size: 1rem;
  font-family: 'Poppins', 'Nunito', sans-serif;
}

.brand-link small {
  display: block;
  font-size: 0.7rem;
  color: var(--color-muted);
}

.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6ee7b7, #38bdf8);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
}

.patient-nav {
  grid-area: nav;
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

@media (max-width: 768px) {
  .nav-toggle {
    display: block;
  }
  .patient-nav {
    display: none;
    flex-direction: column;
    padding: 0.5rem 0;
  }
  .patient-nav.patient-nav--open {
    display: flex;
  }
  .patient-header-actions .user-name {
    display: none;
  }
}

.nav-pill {
  position: relative;
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  text-decoration: none;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-muted);
  white-space: nowrap;
}

.nav-pill.router-link-active {
  background: var(--color-primary-soft, rgba(37, 99, 235, 0.12));
  color: var(--color-primary);
}

.nav-badge {
  margin-left: 0.35rem;
  display: inline-flex;
  min-width: 1.1rem;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: #ef4444;
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.1rem 0.35rem;
  vertical-align: middle;
}

.patient-header-actions {
  grid-area: actions;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.nav-toggle {
  grid-area: toggle;
  display: none;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-muted);
  cursor: pointer;
}

.user-name {
  font-size: 0.85rem;
  color: var(--color-muted);
}

.patient-main {
  flex: 1;
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 2.5rem;
}
</style>
