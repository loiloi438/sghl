<template>
  <div class="hc-page">
    <PatientPageHeader
      title="Hospitalisation"
      subtitle="Vos séjours passés et en cours, avec l’équipe qui vous accompagne"
      module="hospital"
      :loading="loading"
      @refresh="load"
    />

    <div v-if="error" class="hc-alert hc-alert--error">{{ error }}</div>
    <div v-if="loading" class="hc-loading">Chargement de vos hospitalisations…</div>

    <PatientEmptyState
      v-else-if="items.length === 0"
      icon="💙"
      title="Vous êtes en bonne santé"
      text="Aucune hospitalisation enregistrée pour le moment. Nous sommes là si vous avez besoin de nous."
    >
      <RouterLink to="/patient/rendez-vous" class="hc-btn-rdv mt-4 inline-flex">
        Prendre rendez-vous
      </RouterLink>
    </PatientEmptyState>

    <div v-else class="space-y-4">
      <article
        v-for="h in items"
        :key="h.id"
        class="hc-list-item"
        :class="{ 'ring-2 ring-teal-200': h.statut === 'active' }"
      >
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <span
              class="hc-badge"
              :class="h.statut === 'active' ? 'hc-badge--ok' : h.statut === 'terminee' ? 'hc-badge--done' : 'hc-badge--alert'"
            >
              {{ hospitalisationStatutLabel(h.statut) }}
            </span>
            <h2 class="mt-2 text-lg font-bold text-teal-950" style="font-family: Poppins, sans-serif">
              {{ h.motif_admission }}
            </h2>
          </div>
          <span v-if="h.statut === 'active'" class="text-2xl" aria-hidden="true">🏥</span>
        </div>

        <dl class="mt-4 grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt class="text-xs font-bold uppercase tracking-wider text-teal-700">Admission</dt>
            <dd class="mt-0.5 text-slate-700">{{ formatPatientDate(h.date_admission) }}</dd>
          </div>
          <div v-if="h.date_sortie_effective || h.date_sortie_prevue">
            <dt class="text-xs font-bold uppercase tracking-wider text-teal-700">
              {{ h.date_sortie_effective ? 'Sortie' : 'Sortie prévue' }}
            </dt>
            <dd class="mt-0.5 text-slate-700">
              {{ h.date_sortie_effective ? formatPatientDate(h.date_sortie_effective) : formatPatientDateShort(h.date_sortie_prevue) }}
            </dd>
          </div>
          <div>
            <dt class="text-xs font-bold uppercase tracking-wider text-teal-700">Service</dt>
            <dd class="mt-0.5 text-slate-700">{{ h.service_nom || h.service_code }} · {{ h.batiment_code }}</dd>
          </div>
          <div>
            <dt class="text-xs font-bold uppercase tracking-wider text-teal-700">Médecin référent</dt>
            <dd class="mt-0.5 text-slate-700">{{ h.medecin_nom || '—' }}</dd>
          </div>
          <div>
            <dt class="text-xs font-bold uppercase tracking-wider text-teal-700">Chambre / Lit</dt>
            <dd class="mt-0.5 text-slate-700">Ch. {{ h.chambre_numero }} · Lit {{ h.lit_numero }}</dd>
          </div>
        </dl>
      </article>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api, { getErrorMessage, unwrapList } from '../../api/client.js'
import {
  formatPatientDate,
  formatPatientDateShort,
  hospitalisationStatutLabel,
} from '../../composables/usePatientPortal.js'
import PatientEmptyState from '../../components/patient/PatientEmptyState.vue'
import PatientPageHeader from '../../components/patient/PatientPageHeader.vue'

const items = ref([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/patient/hospitalisations/')
    items.value = unwrapList(data)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
