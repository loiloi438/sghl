<template>
  <div class="space-y-6">
    <PatientPageHeader title="Résultats laboratoire" subtitle="Analyses publiées par le laboratoire" :loading="loading" @refresh="load" />

    <div v-if="message" class="rounded-3xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
    <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
    <div v-if="loading" class="rounded-3xl border border-slate-200 bg-white px-6 py-5 text-sm text-slate-600 shadow-sm">Chargement…</div>
    <div v-else-if="items.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-6 py-8 text-center text-sm text-slate-600">Aucun résultat publié.</div>

    <div v-else class="space-y-4">
      <article v-for="r in items" :key="r.id" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <span class="inline-flex rounded-full bg-sky-100 px-3 py-1 text-xs font-semibold text-sky-700">{{ r.statut }}</span>
            <h2 class="mt-3 text-lg font-semibold text-slate-900">Prescrit par Dr {{ r.medecin_nom }}</h2>
            <p class="mt-1 text-sm text-slate-500">Publié le {{ formatPatientDate(r.publiee_le) }}</p>
          </div>
          <button
            type="button"
            class="inline-flex shrink-0 items-center justify-center rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60"
            :disabled="downloadingId === r.id"
            @click="downloadPdf(r)"
          >
            {{ downloadingId === r.id ? 'Téléchargement…' : 'PDF résultats' }}
          </button>
        </div>
        <ul v-if="r.analyses?.length" class="mt-4 space-y-2 text-sm text-slate-700">
          <li v-for="(a, i) in r.analyses" :key="i" class="rounded-2xl bg-slate-50 px-4 py-3 font-mono text-xs leading-6">{{ a }}</li>
        </ul>
      </article>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { downloadPdf as fetchPdf, getErrorMessage, unwrapList } from '../../api/client.js'
import { formatPatientDate } from '../../composables/usePatientPortal.js'
import PatientPageHeader from '../../components/patient/PatientPageHeader.vue'

const items = ref([])
const loading = ref(true)
const error = ref('')
const message = ref('')
const downloadingId = ref(null)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/patient/resultats-laboratoire/')
    items.value = unwrapList(data)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function downloadPdf(r) {
  downloadingId.value = r.id
  message.value = ''
  error.value = ''
  try {
    await fetchPdf(`/commandes-analyses/${r.id}/pdf/`, `labo-${r.id}.pdf`)
    message.value = 'Résultats téléchargés.'
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    downloadingId.value = null
  }
}

onMounted(load)
</script>
