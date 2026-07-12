<template>
  <div class="hc-page">
    <PatientPageHeader
      title="Pharmacie"
      subtitle="Vos prescriptions et leur disponibilité à la pharmacie"
      module="pharmacy"
      :loading="loading"
      @refresh="load"
    />

    <div v-if="message" class="hc-alert hc-alert--success">{{ message }}</div>
    <div v-if="error" class="hc-alert hc-alert--error">{{ error }}</div>
    <div v-if="loading" class="hc-loading">Chargement de vos ordonnances…</div>

    <PatientEmptyState
      v-else-if="items.length === 0"
      icon="💊"
      title="Aucune prescription pour l’instant"
      text="Votre médecin vous transmettra vos ordonnances ici dès qu’elles seront disponibles."
    />

    <div v-else class="space-y-4">
      <article v-for="p in items" :key="p.id" class="hc-list-item">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div class="flex gap-3">
            <span class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-emerald-50 text-2xl">
              {{ pharmacieStatutMeta(p.statut_pharmacie).icon }}
            </span>
            <div>
              <span class="hc-badge" :class="`hc-badge--${pharmacieStatutMeta(p.statut_pharmacie).badge}`">
                {{ pharmacieStatutMeta(p.statut_pharmacie).label }}
              </span>
              <h2 class="mt-2 text-lg font-bold text-teal-950" style="font-family: Poppins, sans-serif">
                Dr {{ p.medecin_nom }}
              </h2>
              <p class="mt-1 text-sm text-slate-500">
                {{ p.validee_le ? `Validée le ${formatPatientDate(p.validee_le)}` : 'En cours de validation' }}
              </p>
            </div>
          </div>
          <button
            v-if="p.statut === 'validee'"
            type="button"
            class="hc-btn-secondary shrink-0"
            :disabled="downloadingId === p.id"
            @click="downloadPdf(p)"
          >
            {{ downloadingId === p.id ? 'Téléchargement…' : '📄 PDF ordonnance' }}
          </button>
        </div>

        <div v-if="p.medicaments?.length" class="mt-4">
          <h3 class="text-xs font-bold uppercase tracking-widest text-teal-700">Médicaments</h3>
          <ul class="mt-2 space-y-2">
            <li
              v-for="(m, i) in p.medicaments"
              :key="i"
              class="rounded-xl bg-emerald-50/60 px-3 py-2 text-sm text-slate-700"
            >
              💊 {{ m }}
            </li>
          </ul>
        </div>

        <div v-if="p.diagnostics?.length" class="mt-4">
          <h3 class="text-xs font-bold uppercase tracking-widest text-teal-700">Diagnostics</h3>
          <ul class="mt-2 list-inside list-disc text-sm text-slate-600">
            <li v-for="(d, i) in p.diagnostics" :key="i">{{ d }}</li>
          </ul>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { downloadPdf as fetchPdf, getErrorMessage, unwrapList } from '../../api/client.js'
import { formatPatientDate, pharmacieStatutMeta } from '../../composables/usePatientPortal.js'
import PatientEmptyState from '../../components/patient/PatientEmptyState.vue'
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
    const { data } = await api.get('/patient/prescriptions/')
    items.value = unwrapList(data)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function downloadPdf(p) {
  downloadingId.value = p.id
  message.value = ''
  error.value = ''
  try {
    await fetchPdf(`/prescriptions/${p.id}/pdf/`, `ordonnance-${p.id}.pdf`)
    message.value = 'Ordonnance téléchargée avec succès.'
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    downloadingId.value = null
  }
}

onMounted(load)
</script>
