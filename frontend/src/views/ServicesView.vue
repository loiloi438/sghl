<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto max-w-7xl space-y-6">
      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Services médicaux</h1>
            <p class="mt-1 text-sm text-slate-600">Organisation des pôles, unités et services hospitaliers</p>
          </div>
          <button class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" type="button" @click="loadAll">Actualiser</button>
        </div>
      </div>

      <div v-if="error" class="rounded-3xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</div>

      <div class="grid gap-4 md:grid-cols-3">
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Bâtiments</span>
          <div class="mt-2 text-3xl font-semibold text-slate-900">{{ batiments.length }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Services</span>
          <div class="mt-2 text-3xl font-semibold text-slate-900">{{ filteredServices.length }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Filtre</span>
          <div class="mt-2 text-lg font-semibold text-slate-900">{{ selectedBatimentLabel }}</div>
        </article>
      </div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="grid gap-4 lg:grid-cols-[1.4fr_0.6fr] lg:items-end">
          <input v-model="search" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" type="search" placeholder="Rechercher un service…" @input="debouncedLoad" />
          <select v-model="batimentFilter" @change="loadAll" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500">
            <option value="">Tous les bâtiments</option>
            <option v-for="b in batiments" :key="b.id" :value="b.id">{{ b.code }} — {{ b.nom }}</option>
          </select>
        </div>

        <div v-if="loading" class="mt-6 text-sm text-slate-500">Chargement…</div>
        <div v-else-if="filteredServices.length === 0" class="mt-6 text-sm text-slate-500">Aucun service trouvé.</div>

        <div v-else class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <article v-for="service in filteredServices" :key="service.id" class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
            <div class="flex items-center justify-between gap-3">
              <span class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">{{ service.batiment_code }}</span>
              <span :class="service.actif ? 'rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700' : 'rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600'">{{ service.actif ? 'Actif' : 'Inactif' }}</span>
            </div>
            <h2 class="mt-4 text-lg font-semibold text-slate-900">{{ service.nom }}</h2>
            <p class="mt-2 text-sm text-slate-500">{{ service.code }}</p>
          </article>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api, { getErrorMessage, unwrapList } from '../api/client.js'

const batiments = ref([])
const services = ref([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const batimentFilter = ref('')
let timer

const selectedBatimentLabel = computed(() => {
  if (!batimentFilter.value) return 'Tous'
  const b = batiments.value.find((item) => item.id === batimentFilter.value)
  return b ? `${b.code}` : 'Filtre appliqué'
})

const filteredServices = computed(() => {
  const needle = search.value.trim().toLowerCase()
  return services.value.filter((service) => {
    const matchesSearch = !needle || [service.nom, service.code, service.batiment_code].some((value) =>
      String(value || '').toLowerCase().includes(needle),
    )
    const matchesBatiment = !batimentFilter.value || service.batiment_id === batimentFilter.value
    return matchesSearch && matchesBatiment
  })
})

function debouncedLoad() {
  clearTimeout(timer)
  timer = setTimeout(loadAll, 300)
}

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const [batimentsRes, servicesRes] = await Promise.all([
      api.get('/services/batiments/'),
      api.get('/services/'),
    ])
    batiments.value = unwrapList(batimentsRes.data)
    services.value = unwrapList(servicesRes.data)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)
</script>