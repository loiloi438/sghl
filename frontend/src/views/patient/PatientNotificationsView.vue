<template>
  <div class="space-y-6">
    <PatientPageHeader title="Notifications" :subtitle="unreadCount ? `${unreadCount} non lue(s)` : 'Tout est à jour'" :loading="loading" @refresh="load" />

    <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
    <div v-if="loading" class="rounded-3xl border border-slate-200 bg-white px-6 py-5 text-sm text-slate-600 shadow-sm">Chargement…</div>
    <div v-else-if="items.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-6 py-8 text-center text-sm text-slate-600">Aucune notification pour le moment.</div>

    <div v-else class="space-y-3">
      <article
        v-for="n in items"
        :key="n.id"
        class="rounded-3xl border p-5 shadow-sm transition"
        :class="n.lu ? 'border-slate-200 bg-white' : 'border-sky-200 bg-sky-50'"
      >
        <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <h2 class="font-semibold text-slate-900">{{ n.titre }}</h2>
              <span v-if="!n.lu" class="rounded-full bg-sky-600 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white">Nouveau</span>
              <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-500">{{ n.categorie }}</span>
            </div>
            <p class="mt-2 text-sm leading-6 text-slate-700">{{ n.corps }}</p>
            <p class="mt-2 text-xs text-slate-500">{{ formatPatientDate(n.created_at) }}</p>
          </div>
          <button
            v-if="!n.lu"
            type="button"
            class="shrink-0 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
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
import { formatPatientDate } from '../../composables/usePatientPortal.js'
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
