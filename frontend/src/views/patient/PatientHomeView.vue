<template>
  <div class="space-y-6">
    <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Mon espace</h1>
          <p class="mt-1 text-sm text-slate-600">Bienvenue{{ profil ? `, ${profil.prenom}` : '' }}</p>
        </div>
        <button
          class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
          type="button"
          :disabled="loading"
          @click="load"
        >
          Actualiser
        </button>
      </div>
    </div>

    <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 shadow-sm">{{ error }}</div>
    <div v-if="loading" class="rounded-3xl border border-slate-200 bg-white px-6 py-5 text-sm text-slate-600 shadow-sm">Chargement…</div>

    <template v-else-if="dashboard">
      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-xl font-semibold text-slate-900">{{ profil.prenom }} {{ profil.nom }}</h2>
        <p class="mt-1 text-sm text-slate-500">Dossier {{ profil.numero_dossier }}</p>

        <div class="mt-6 grid gap-4 sm:grid-cols-3">
          <article class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Hospitalisation</span>
            <p class="mt-2 text-sm font-semibold text-slate-900">{{ dashboard.hospitalisation_active ? 'En cours' : 'Aucune' }}</p>
          </article>
          <article class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Doses à venir</span>
            <p class="mt-2 text-2xl font-semibold text-slate-900">{{ dashboard.prochaines_doses?.length || 0 }}</p>
          </article>
          <article class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Constantes récentes</span>
            <p class="mt-2 text-2xl font-semibold text-slate-900">{{ dashboard.constantes_recentes?.length || 0 }}</p>
          </article>
        </div>

        <RouterLink
          to="/patient/rendez-vous"
          class="mt-6 inline-flex items-center justify-center rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Prendre un rendez-vous
        </RouterLink>
      </section>

      <section v-if="dashboard.hospitalisation_active" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 class="text-lg font-semibold text-slate-900">Hospitalisation en cours</h3>
        <p class="mt-3 text-sm leading-6 text-slate-700">{{ dashboard.hospitalisation_active.motif_admission }}</p>
        <p class="mt-4 text-sm text-slate-500">
          Lit {{ dashboard.hospitalisation_active.batiment_code }}/{{ dashboard.hospitalisation_active.service_code }} — Ch. {{ dashboard.hospitalisation_active.chambre_numero }}
        </p>
      </section>

      <section>
        <h3 class="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Accès rapide</h3>
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <RouterLink
            v-for="card in shortcutCards"
            :key="card.to"
            :to="card.to"
            class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md"
          >
            <span class="text-2xl">{{ card.icon }}</span>
            <span class="mt-3 block text-sm font-semibold text-slate-900">{{ card.label }}</span>
          </RouterLink>
        </div>
      </section>

      <section v-if="dashboard.prochaines_doses?.length" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex items-center justify-between gap-3">
          <h3 class="text-lg font-semibold text-slate-900">Prochains médicaments</h3>
          <RouterLink to="/patient/soins" class="text-sm font-semibold text-blue-600 hover:text-blue-700">Tout voir →</RouterLink>
        </div>
        <ul class="mt-4 space-y-3">
          <li
            v-for="d in dashboard.prochaines_doses"
            :key="d.id"
            class="rounded-2xl border px-4 py-3 text-sm"
            :class="d.est_en_retard ? 'border-rose-200 bg-rose-50' : 'border-slate-200 bg-slate-50'"
          >
            <strong class="text-slate-900">{{ d.medicament }}</strong>
            <span class="text-slate-600"> — {{ d.posologie }}</span>
            <p class="mt-1 text-xs text-slate-500">{{ formatPatientDate(d.heure_prevue) }}</p>
          </li>
        </ul>
      </section>

      <section v-if="dashboard.constantes_recentes?.length" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex items-center justify-between gap-3">
          <h3 class="text-lg font-semibold text-slate-900">Constantes récentes</h3>
          <RouterLink to="/patient/soins" class="text-sm font-semibold text-blue-600 hover:text-blue-700">Historique →</RouterLink>
        </div>
        <ul class="mt-4 space-y-3">
          <li v-for="c in dashboard.constantes_recentes" :key="c.id" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
            {{ constanteSummary(c) }}
            <p class="mt-1 text-xs text-slate-500">{{ formatPatientDate(c.mesure_le) }}</p>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api, { getErrorMessage } from '../../api/client.js'
import { constanteSummary, formatPatientDate } from '../../composables/usePatientPortal.js'

const loading = ref(true)
const error = ref('')
const dashboard = ref(null)

const profil = computed(() => dashboard.value?.profil)

const shortcutCards = [
  { to: '/patient/soins', label: 'Soins & constantes', icon: '🩺' },
  { to: '/patient/prescriptions', label: 'Prescriptions', icon: '💊' },
  { to: '/patient/laboratoire', label: 'Laboratoire', icon: '🔬' },
  { to: '/patient/factures', label: 'Factures', icon: '🧾' },
  { to: '/patient/rendez-vous', label: 'Rendez-vous', icon: '📅' },
  { to: '/patient/notifications', label: 'Notifications', icon: '🔔' },
  { to: '/patient/profil', label: 'Mon profil', icon: '👤' },
  { to: '/contact', label: 'Contact & accès', icon: '📍' },
]

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/patient/tableau-de-bord/')
    dashboard.value = data
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
