<template>
  <div class="space-y-6">
    <PatientPageHeader title="Suivi des soins" subtitle="Constantes vitales, plans de soins et médicaments" :loading="loading" @refresh="loadAll" />

    <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>

    <div class="flex flex-wrap gap-2 rounded-3xl bg-slate-50 p-2">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        class="rounded-2xl px-4 py-2 text-sm font-semibold transition"
        :class="activeTab === tab.id ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-100'"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="rounded-3xl border border-slate-200 bg-white px-6 py-5 text-sm text-slate-600 shadow-sm">Chargement…</div>

    <div v-else-if="activeTab === 'constantes'">
      <div v-if="constantes.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-6 py-8 text-center text-sm text-slate-600">Aucune constante enregistrée.</div>
      <div v-else class="space-y-3">
        <article v-for="c in constantes" :key="c.id" class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm font-semibold text-slate-900">{{ constanteSummary(c) }}</p>
          <p class="mt-2 text-xs text-slate-500">{{ formatPatientDate(c.mesure_le) }}</p>
        </article>
      </div>
    </div>

    <div v-else-if="activeTab === 'plans'">
      <div v-if="plans.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-6 py-8 text-center text-sm text-slate-600">Aucun plan de soins.</div>
      <div v-else class="space-y-3">
        <article v-for="p in plans" :key="p.id" class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-center justify-between gap-3">
            <h2 class="text-base font-semibold text-slate-900">{{ p.titre }}</h2>
            <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">{{ p.statut }}</span>
          </div>
          <p class="mt-2 text-sm text-slate-600">{{ p.description || '—' }}</p>
          <p class="mt-3 text-xs text-slate-500">Début : {{ formatPatientDate(p.date_debut) }}</p>
        </article>
      </div>
    </div>

    <div v-else>
      <div v-if="doses.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-6 py-8 text-center text-sm text-slate-600">Aucune dose planifiée.</div>
      <div v-else class="space-y-3">
        <article
          v-for="d in doses"
          :key="d.id"
          class="rounded-3xl border p-5 shadow-sm"
          :class="d.est_en_retard ? 'border-rose-200 bg-rose-50' : 'border-slate-200 bg-white'"
        >
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h2 class="font-semibold text-slate-900">{{ d.medicament }}</h2>
            <span v-if="d.est_en_retard" class="rounded-full bg-rose-600 px-3 py-1 text-xs font-semibold text-white">En retard</span>
            <span v-else class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">{{ d.statut }}</span>
          </div>
          <p class="mt-2 text-sm text-slate-600">{{ d.posologie }}</p>
          <p class="mt-2 text-xs text-slate-500">Prévu : {{ formatPatientDate(d.heure_prevue) }}</p>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { getErrorMessage, unwrapList } from '../../api/client.js'
import { constanteSummary, formatPatientDate } from '../../composables/usePatientPortal.js'
import PatientPageHeader from '../../components/patient/PatientPageHeader.vue'

const tabs = [
  { id: 'constantes', label: 'Constantes' },
  { id: 'plans', label: 'Plans de soins' },
  { id: 'doses', label: 'Médicaments' },
]

const activeTab = ref('constantes')
const loading = ref(true)
const error = ref('')
const constantes = ref([])
const plans = ref([])
const doses = ref([])

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const [cRes, pRes, dRes] = await Promise.all([
      api.get('/patient/constantes-vitales/'),
      api.get('/patient/plans-soins/'),
      api.get('/patient/doses/'),
    ])
    constantes.value = unwrapList(cRes.data)
    plans.value = unwrapList(pRes.data)
    doses.value = unwrapList(dRes.data)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)
</script>
