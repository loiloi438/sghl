<template>
  <div class="hc-page">
    <PatientPageHeader
      title="Laboratoire"
      subtitle="Résultats d’analyses et évolution de vos indicateurs de santé"
      module="lab"
      :loading="loading"
      @refresh="loadAll"
    />

    <div v-if="message" class="hc-alert hc-alert--success">{{ message }}</div>
    <div v-if="error" class="hc-alert hc-alert--error">{{ error }}</div>
    <div v-if="loading" class="hc-loading">Chargement…</div>

    <template v-else>
      <section v-if="glycemieSeries.length || tensionSeries.length" class="hc-card hc-card-padded space-y-6">
        <h2 class="font-bold text-teal-900" style="font-family: Poppins, sans-serif">Évolution de vos constantes</h2>

        <div v-if="glycemieSeries.length" class="rounded-2xl border border-sky-100 bg-sky-50/50 p-4">
          <h3 class="text-sm font-bold text-sky-800">Glycémie (g/L)</h3>
          <SimpleBarChart :series="glycemieSeries" aria-label="Graphique glycémie" />
        </div>

        <div v-if="tensionSeries.length" class="rounded-2xl border border-violet-100 bg-violet-50/50 p-4">
          <h3 class="text-sm font-bold text-violet-800">Tension systolique (mmHg)</h3>
          <SimpleBarChart :series="tensionSeries" aria-label="Graphique tension" />
        </div>
      </section>

      <section>
        <h2 class="mb-3 text-sm font-bold uppercase tracking-widest text-teal-800">Résultats publiés</h2>

        <PatientEmptyState
          v-if="items.length === 0"
          icon="🔬"
          title="Aucun résultat publié"
          text="Vos analyses apparaîtront ici dès leur validation par le laboratoire."
        />

        <div v-else class="space-y-4">
          <article v-for="r in items" :key="r.id" class="hc-list-item">
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <span class="hc-badge hc-badge--done">Publié</span>
                <h3 class="mt-2 text-lg font-bold text-teal-950" style="font-family: Poppins, sans-serif">
                  Dr {{ r.medecin_nom }}
                </h3>
                <p class="mt-1 text-sm text-slate-500">Publié le {{ formatPatientDate(r.publiee_le) }}</p>
              </div>
              <button
                type="button"
                class="hc-btn-secondary shrink-0"
                :disabled="downloadingId === r.id"
                @click="downloadPdf(r)"
              >
                {{ downloadingId === r.id ? 'Téléchargement…' : '📄 PDF résultats' }}
              </button>
            </div>
            <ul v-if="r.analyses?.length" class="mt-4 space-y-2">
              <li
                v-for="(a, i) in r.analyses"
                :key="i"
                class="rounded-xl bg-sky-50/70 px-4 py-3 font-mono text-xs leading-6 text-slate-700"
              >
                {{ a }}
              </li>
            </ul>
          </article>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api, { downloadPdf as fetchPdf, getErrorMessage, unwrapList } from '../../api/client.js'
import { formatPatientDate, formatPatientDateShort } from '../../composables/usePatientPortal.js'
import PatientEmptyState from '../../components/patient/PatientEmptyState.vue'
import PatientPageHeader from '../../components/patient/PatientPageHeader.vue'
import SimpleBarChart from '../../components/SimpleBarChart.vue'

const items = ref([])
const constantes = ref([])
const loading = ref(true)
const error = ref('')
const message = ref('')
const downloadingId = ref(null)

const glycemieSeries = computed(() =>
  [...constantes.value]
    .filter((c) => c.glycemie != null)
    .slice(0, 8)
    .reverse()
    .map((c) => ({
      label: formatPatientDateShort(c.mesure_le),
      value: Number(c.glycemie),
    })),
)

const tensionSeries = computed(() =>
  [...constantes.value]
    .filter((c) => c.tension_systolique != null)
    .slice(0, 8)
    .reverse()
    .map((c) => ({
      label: formatPatientDateShort(c.mesure_le),
      value: c.tension_systolique,
    })),
)

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const [labRes, constRes] = await Promise.all([
      api.get('/patient/resultats-laboratoire/'),
      api.get('/patient/constantes-vitales/'),
    ])
    items.value = unwrapList(labRes.data)
    constantes.value = unwrapList(constRes.data)
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

onMounted(loadAll)
</script>
