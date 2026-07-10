<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto max-w-7xl space-y-6">
      <header class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Statistiques & Rapports</h1>
            <p class="mt-1 text-sm text-slate-600">Analyse de l’activité clinique et exports de synthèse</p>
          </div>
          <button @click="loadReport" class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-100">Actualiser</button>
        </div>
      </header>

      <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="grid gap-4 lg:grid-cols-[1.12fr_0.88fr]">
          <div class="grid gap-4 sm:grid-cols-2">
            <label class="space-y-2">
              <span class="text-sm font-semibold text-slate-700">Date de début</span>
              <input id="date-debut" v-model="filters.startDate" type="date" @change="loadReport" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100" />
            </label>
            <label class="space-y-2">
              <span class="text-sm font-semibold text-slate-700">Date de fin</span>
              <input id="date-fin" v-model="filters.endDate" type="date" @change="loadReport" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100" />
            </label>
          </div>
          <div class="flex flex-col justify-between rounded-3xl border border-slate-200 bg-slate-50 p-4">
            <div>
              <p class="text-sm font-semibold text-slate-700">Exports</p>
              <p class="mt-1 text-sm text-slate-500">Téléchargez le rapport en PDF ou CSV.</p>
            </div>
            <div class="mt-4 flex flex-col gap-3 sm:flex-row sm:justify-end">
              <button @click="exportPdf" class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800">PDF</button>
              <button @click="exportCsv" class="rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">CSV</button>
            </div>
          </div>
        </div>
      </section>

      <section v-if="loading" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm text-sm text-slate-600">Chargement…</section>

      <template v-else>
        <section class="grid gap-4 xl:grid-cols-3">
          <article v-for="card in kpis" :key="card.label" class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{{ card.label }}</span>
            <div class="mt-3 text-3xl font-semibold text-slate-900">{{ card.value }}</div>
            <p class="mt-3 text-sm leading-6 text-slate-500">{{ card.help }}</p>
          </article>
        </section>

        <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="mb-6">
            <h2 class="text-lg font-semibold text-slate-900">Activité journalière</h2>
            <p class="mt-1 text-sm text-slate-500">Admissions, rendez-vous, prescriptions et factures par jour</p>
          </div>
          <SimpleBarChart :series="activitySeries" aria-label="Évolution journalière de l'activité" />
        </section>

        <section class="grid gap-4 xl:grid-cols-2">
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">Admissions par service</h2>
            <div class="mt-4 overflow-x-auto">
              <table class="min-w-full divide-y divide-slate-200 text-sm">
                <thead class="bg-slate-50 text-slate-500">
                  <tr>
                    <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.15em]">Service</th>
                    <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.15em]">Code</th>
                    <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.15em]">Admissions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-200 bg-white">
                  <tr v-for="row in report.hospitalisations_par_service" :key="row.code_service + row.service" class="hover:bg-slate-50">
                    <td class="px-4 py-4 text-slate-700">{{ row.service }}</td>
                    <td class="px-4 py-4 text-slate-700">{{ row.code_service }}</td>
                    <td class="px-4 py-4 text-slate-700">{{ row.count }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">Répartition par statut</h2>
            <div class="mt-6 grid gap-4 sm:grid-cols-3">
              <div>
                <p class="text-sm font-semibold text-slate-800">Rendez-vous</p>
                <ul class="mt-3 space-y-2 text-sm text-slate-600">
                  <li v-for="row in report.rendez_vous_par_statut" :key="row.statut">{{ labelStatut(row.statut) }}: {{ row.count }}</li>
                </ul>
              </div>
              <div>
                <p class="text-sm font-semibold text-slate-800">Factures</p>
                <ul class="mt-3 space-y-2 text-sm text-slate-600">
                  <li v-for="row in report.factures_par_statut" :key="row.statut">{{ labelStatut(row.statut) }}: {{ row.count }}</li>
                </ul>
              </div>
              <div>
                <p class="text-sm font-semibold text-slate-800">Prescriptions</p>
                <ul class="mt-3 space-y-2 text-sm text-slate-600">
                  <li v-for="row in report.prescriptions_par_statut" :key="row.statut">{{ labelStatut(row.statut) }}: {{ row.count }}</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="mb-6">
            <h2 class="text-lg font-semibold text-slate-900">Table d’activité</h2>
            <p class="mt-1 text-sm text-slate-500">Détail quotidien exploitable en audit ou soutenance</p>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200 text-sm">
              <thead class="bg-slate-50 text-slate-500">
                <tr>
                  <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.15em]">Date</th>
                  <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.15em]">Admissions</th>
                  <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.15em]">Rendez-vous</th>
                  <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.15em]">Prescriptions</th>
                  <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.15em]">Factures</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 bg-white">
                <tr v-for="row in report.evolution_journaliere" :key="row.date" class="hover:bg-slate-50">
                  <td class="px-4 py-4 text-slate-700">{{ formatDate(row.date) }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ row.admissions }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ row.rendez_vous }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ row.prescriptions }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ row.factures }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import api, { downloadBlob, downloadPdf, getErrorMessage } from '../api/client.js'
import SimpleBarChart from '../components/SimpleBarChart.vue'

const loading = ref(true)
const error = ref('')
const report = ref(null)
const filters = reactive({
  startDate: '',
  endDate: '',
})

const kpis = computed(() => {
  if (!report.value) return []
  const k = report.value.kpis
  return [
    { label: 'Admissions', value: k.admissions, help: 'Hospitalisations démarrées sur la période' },
    { label: 'Rendez-vous', value: k.rendez_vous, help: 'Consultations planifiées ou confirmées' },
    { label: 'Prescriptions', value: k.prescriptions, help: 'Ordonnances créées' },
    { label: 'Factures', value: k.factures, help: 'Documents comptables générés' },
    { label: 'Occupation lits', value: `${k.taux_occupation} %`, help: `${k.lits_occupes} / ${k.lits_actifs} lits` },
    { label: 'Factures payées', value: k.factures_payees, help: 'État de paiement finalisé' },
  ]
})

const activitySeries = computed(() => {
  if (!report.value) return []
  return report.value.evolution_journaliere.map((row) => ({
    label: new Date(row.date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }),
    value: row.admissions + row.rendez_vous + row.prescriptions + row.factures,
  }))
})

function formatDate(value) {
  try {
    return new Date(value).toLocaleDateString('fr-FR')
  } catch {
    return value
  }
}

function labelStatut(value) {
  return {
    planifie: 'Planifié',
    confirme: 'Confirmé',
    annule: 'Annulé',
    termine: 'Terminé',
    absent: 'Absent',
    brouillon: 'Brouillon',
    validee: 'Validée',
    partiellement_payee: 'Partiellement payée',
    payee: 'Payée',
    annulee: 'Annulée',
  }[value] || value
}

function paramsQuery() {
  const params = new URLSearchParams()
  if (filters.startDate) params.set('start_date', filters.startDate)
  if (filters.endDate) params.set('end_date', filters.endDate)
  return params.toString()
}

async function loadReport() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/statistiques/rapport/${paramsQuery() ? `?${paramsQuery()}` : ''}`)
    report.value = data
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function exportPdf() {
  try {
    await downloadPdf(
      `/statistiques/rapport/pdf/${paramsQuery() ? `?${paramsQuery()}` : ''}`,
      `rapport-statistiques-${filters.startDate || 'debut'}-${filters.endDate || 'fin'}.pdf`,
    )
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function exportCsv() {
  try {
    await downloadBlob(
      `/statistiques/rapport/csv/${paramsQuery() ? `?${paramsQuery()}` : ''}`,
      `rapport-statistiques-${filters.startDate || 'debut'}-${filters.endDate || 'fin'}.csv`,
      'text/csv;charset=utf-8',
    )
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

onMounted(async () => {
  const today = new Date()
  filters.endDate = today.toISOString().slice(0, 10)
  filters.startDate = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().slice(0, 10)
  await loadReport()
})
</script>
