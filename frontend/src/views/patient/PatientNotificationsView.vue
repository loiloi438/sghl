<template>
  <div class="hc-page">
    <PatientPageHeader
      title="Notifications"
      :subtitle="unreadCount ? `${unreadCount} message(s) à lire` : 'Tout est à jour — bonne journée 💙'"
      module="notification"
      :loading="loading"
      @refresh="load"
    />

    <div v-if="error" class="hc-alert hc-alert--error">{{ error }}</div>
    <div v-if="loading" class="hc-loading">Chargement…</div>

    <PatientEmptyState
      v-else-if="items.length === 0"
      icon="🔔"
      title="Aucune notification"
      text="Les rappels de rendez-vous et messages du secrétariat apparaîtront ici."
    />

    <div v-else class="space-y-3">
      <article
        v-for="n in items"
        :key="n.id"
        class="hc-list-item transition"
        :class="n.lu ? '' : 'border-sky-200 bg-sky-50/60'"
      >
        <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div class="flex gap-3">
            <span class="text-2xl">{{ notificationCategorieMeta(n.categorie).icon }}</span>
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <h2 class="font-bold text-slate-900">{{ n.titre }}</h2>
                <span v-if="!n.lu" class="hc-badge hc-badge--pending">Nouveau</span>
                <span class="hc-badge hc-badge--done">{{ notificationCategorieMeta(n.categorie).label }}</span>
              </div>
              <p class="mt-2 text-sm leading-relaxed text-slate-700">{{ n.corps }}</p>
              <p class="mt-2 text-xs text-slate-500">{{ formatPatientDate(n.created_at) }}</p>
            </div>
          </div>
          <button
            v-if="!n.lu"
            type="button"
            class="hc-btn-secondary shrink-0"
            @click="markRead(n)"
          >
            Marquer comme lu
          </button>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { getErrorMessage, unwrapList } from '../../api/client.js'
import { formatPatientDate, notificationCategorieMeta } from '../../composables/usePatientPortal.js'
import PatientEmptyState from '../../components/patient/PatientEmptyState.vue'
import PatientPageHeader from '../../components/patient/PatientPageHeader.vue'

const items = ref([])
const unreadCount = ref(0)
const loading = ref(true)
const error = ref('')

async function loadUnread() {
  try {
    const { data } = await api.get('/patient/notifications/non-lues/')
    unreadCount.value = data.count ?? 0
  } catch {
    unreadCount.value = 0
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/patient/notifications/')
    items.value = unwrapList(data)
    await loadUnread()
    window.dispatchEvent(new CustomEvent('patient-notifications-updated', { detail: { count: unreadCount.value } }))
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function markRead(n) {
  try {
    await api.post(`/patient/notifications/${n.id}/lu/`)
    n.lu = true
    await loadUnread()
    window.dispatchEvent(new CustomEvent('patient-notifications-updated', { detail: { count: unreadCount.value } }))
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

onMounted(load)
</script>
