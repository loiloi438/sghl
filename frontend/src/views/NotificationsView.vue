<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <div class="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Notifications</h1>
          <p class="mt-1 text-sm text-slate-600">Centre de notifications staff et alertes opérationnelles</p>
        </div>
        <button class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" type="button" @click="loadAll">Actualiser</button>
      </div>

      <div v-if="error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</div>

      <div class="grid gap-4 md:grid-cols-3">
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Non lues</span>
          <div class="mt-2 text-3xl font-semibold text-slate-900">{{ unreadCount }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Total affiché</span>
          <div class="mt-2 text-3xl font-semibold text-slate-900">{{ notifications.length }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Filtre</span>
          <div class="mt-2 text-lg font-semibold text-slate-900">{{ filterLabel }}</div>
        </article>
      </div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <input v-model="search" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500 md:max-w-md" type="search" placeholder="Rechercher une notification…" @input="debouncedLoad" />
          <select v-model="stateFilter" @change="loadAll" class="rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500">
            <option value="all">Toutes</option>
            <option value="unread">Non lues</option>
            <option value="read">Lues</option>
          </select>
        </div>

        <div v-if="loading" class="text-sm text-slate-500">Chargement…</div>
        <div v-else-if="notifications.length === 0" class="text-sm text-slate-500">Aucune notification.</div>
        <div v-else class="flex flex-col gap-3">
          <article v-for="notification in notifications" :key="notification.id" class="rounded-3xl border border-slate-200 p-5" :class="!notification.lu ? 'bg-blue-50/70' : 'bg-white'">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <h2 class="text-base font-semibold text-slate-900">{{ notification.titre }}</h2>
                  <span v-if="!notification.lu" class="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-700">Non lue</span>
                  <span v-else class="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">Lue</span>
                </div>
                <p class="mt-1 text-sm text-slate-500">
                  {{ formatDate(notification.created_at) }}
                  <span v-if="notification.categorie">· {{ notification.categorie }}</span>
                </p>
              </div>
              <button v-if="!notification.lu" class="rounded-2xl bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-700" type="button" @click="markRead(notification.id)">
                Marquer lue
              </button>
            </div>

            <p class="mt-4 text-sm leading-6 text-slate-700">{{ notification.corps }}</p>

            <div v-if="notification.donnees && Object.keys(notification.donnees).length > 0" class="mt-4 flex flex-wrap gap-2">
              <span v-for="(value, key) in notification.donnees" :key="key" class="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs text-slate-600">
                {{ key }}: {{ value }}
              </span>
            </div>
          </article>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api, { getErrorMessage, unwrapList } from '../api/client.js'

const notifications = ref([])
const unreadCount = ref(0)
const loading = ref(true)
const error = ref('')
const search = ref('')
const stateFilter = ref('all')
let searchTimer

const filterLabel = computed(() => {
  if (stateFilter.value === 'unread') return 'Non lues'
  if (stateFilter.value === 'read') return 'Lues'
  return 'Toutes'
})

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('fr-FR')
  } catch {
    return iso
  }
}

function debouncedLoad() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadAll, 300)
}

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (search.value) params.set('search', search.value)
    if (stateFilter.value === 'unread') params.set('lu', 'false')
    if (stateFilter.value === 'read') params.set('lu', 'true')

    const [listResponse, countResponse] = await Promise.all([
      api.get(`/notifications/${params.toString() ? `?${params.toString()}` : ''}`),
      api.get('/notifications/non-lues/'),
    ])

    notifications.value = unwrapList(listResponse.data)
    unreadCount.value = countResponse.data.count || 0
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function markRead(notificationId) {
  try {
    await api.post(`/notifications/${notificationId}/lu/`)
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

onMounted(loadAll)
</script>

