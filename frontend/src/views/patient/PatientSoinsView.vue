<template>
  <div class="hc-page">
    <PatientPageHeader
      title="Soins infirmiers"
      subtitle="Planning des soins, constantes vitales et suivi personnalisé"
      module="care"
      :loading="loading"
      @refresh="loadAll"
    />

    <div v-if="error" class="hc-alert hc-alert--error">{{ error }}</div>

    <div class="hc-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        class="hc-tab"
        :class="{ 'hc-tab--active': activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="hc-loading">Chargement…</div>

    <div v-else-if="activeTab === 'planning'">
      <PatientEmptyState
        v-if="doses.length === 0"
        icon="🩺"
        title="Aucun soin planifié"
        text="Votre infirmière vous informera dès qu’un nouveau soin sera programmé."
      />
      <div v-else class="space-y-3">
        <article
          v-for="d in doses"
          :key="d.id"
          class="hc-list-item"
          :class="d.est_en_retard ? 'border-rose-200 bg-rose-50/50' : ''"
        >
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="flex items-center gap-2">
              <span class="text-xl">💉</span>
              <h2 class="font-bold text-slate-900">{{ d.medicament }}</h2>
            </div>
            <span class="hc-badge" :class="`hc-badge--${doseStatutMeta(d).badge}`">
              {{ doseStatutMeta(d).icon }} {{ doseStatutMeta(d).label }}
            </span>
          </div>
          <p class="mt-2 text-sm text-slate-600">{{ d.posologie }}</p>
          <div class="mt-3 flex flex-wrap gap-4 text-xs text-slate-500">
            <span>🕐 {{ formatPatientDate(d.heure_prevue) }}</span>
            <span v-if="d.infirmier_nom">👩‍⚕️ {{ d.infirmier_nom }}</span>
          </div>
        </article>
      </div>
    </div>

    <div v-else-if="activeTab === 'constantes'">
      <PatientEmptyState
        v-if="constantes.length === 0"
        icon="💙"
        title="Pas encore de constantes"
        text="Vos mesures apparaîtront ici après votre prochain passage aux soins."
      />
      <div v-else class="space-y-3">
        <article v-for="c in constantes" :key="c.id" class="hc-list-item">
          <p class="font-semibold text-slate-900">{{ constanteSummary(c) }}</p>
          <p class="mt-2 text-xs text-slate-500">
            {{ formatPatientDate(c.mesure_le) }}
            <span v-if="c.infirmier_nom"> · {{ c.infirmier_nom }}</span>
          </p>
        </article>
      </div>
    </div>

    <div v-else>
      <PatientEmptyState
        v-if="plans.length === 0"
        icon="📋"
        title="Aucun plan de soins"
        text="Votre équipe soignante élabore un plan adapté à vos besoins."
      />
      <div v-else class="space-y-3">
        <article v-for="p in plans" :key="p.id" class="hc-list-item">
          <div class="flex items-center justify-between gap-3">
            <h2 class="font-bold text-slate-900">{{ p.titre }}</h2>
            <span class="hc-badge hc-badge--ok">{{ p.statut }}</span>
          </div>
          <p class="mt-2 text-sm text-slate-600">{{ p.description || '—' }}</p>
          <p class="mt-3 text-xs text-slate-500">
            Début : {{ formatPatientDate(p.date_debut) }}
            <span v-if="p.infirmier_nom"> · {{ p.infirmier_nom }}</span>
          </p>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { getErrorMessage, unwrapList } from '../../api/client.js'
import {
  constanteSummary,
  doseStatutMeta,
  formatPatientDate,
} from '../../composables/usePatientPortal.js'
import PatientEmptyState from '../../components/patient/PatientEmptyState.vue'
import PatientPageHeader from '../../components/patient/PatientPageHeader.vue'

const tabs = [
  { id: 'planning', label: 'Planning des soins' },
  { id: 'constantes', label: 'Constantes' },
  { id: 'plans', label: 'Plans de soins' },
]

const activeTab = ref('planning')
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
