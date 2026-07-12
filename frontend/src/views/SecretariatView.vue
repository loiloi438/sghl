<template>
  <div class="min-h-screen bg-gradient-to-b from-teal-50/80 to-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <header class="rounded-3xl border border-teal-100 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p class="text-sm font-semibold text-teal-700">🌿 Secrétariat SGHL</p>
            <h1 class="mt-1 text-2xl font-bold tracking-tight text-teal-950">Bonjour {{ auth.fullName || 'Samantha' }} 👋</h1>
            <p class="mt-1 text-sm text-slate-600">Rendez-vous, caisse et messagerie patients — tout en un seul endroit.</p>
          </div>
          <button
            type="button"
            class="rounded-2xl border border-teal-200 bg-teal-50 px-4 py-2.5 text-sm font-semibold text-teal-800 transition hover:bg-teal-100"
            @click="loadAll"
          >
            Actualiser
          </button>
        </div>
      </header>

      <div v-if="message" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{{ message }}</div>
      <div v-if="error" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{{ error }}</div>

      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <article class="rounded-3xl border border-amber-100 bg-amber-50/80 p-5 shadow-sm">
          <span class="text-xs font-bold uppercase tracking-widest text-amber-800">En attente</span>
          <div class="mt-2 text-3xl font-bold text-amber-950">{{ stats.rdv_en_attente ?? 0 }}</div>
          <p class="mt-1 text-xs text-amber-900/70">Demandes patient à valider</p>
        </article>
        <article class="rounded-3xl border border-emerald-100 bg-emerald-50/80 p-5 shadow-sm">
          <span class="text-xs font-bold uppercase tracking-widest text-emerald-800">Validés</span>
          <div class="mt-2 text-3xl font-bold text-emerald-950">{{ stats.rdv_valides ?? 0 }}</div>
          <p class="mt-1 text-xs text-emerald-900/70">Rendez-vous confirmés à venir</p>
        </article>
        <article class="rounded-3xl border border-rose-100 bg-rose-50/80 p-5 shadow-sm">
          <span class="text-xs font-bold uppercase tracking-widest text-rose-800">Annulés</span>
          <div class="mt-2 text-3xl font-bold text-rose-950">{{ stats.rdv_annules ?? 0 }}</div>
          <p class="mt-1 text-xs text-rose-900/70">Total annulations</p>
        </article>
        <article class="rounded-3xl border border-sky-100 bg-sky-50/80 p-5 shadow-sm">
          <span class="text-xs font-bold uppercase tracking-widest text-sky-800">Aujourd'hui</span>
          <div class="mt-2 text-3xl font-bold text-sky-950">{{ stats.rdv_aujourdhui ?? 0 }}</div>
          <p class="mt-1 text-xs text-sky-900/70">Consultations du jour</p>
        </article>
      </div>

      <div class="grid gap-4 md:grid-cols-3">
        <RouterLink
          to="/caisse"
          class="rounded-3xl border border-teal-100 bg-white p-5 shadow-sm transition hover:border-teal-300 hover:shadow-md"
        >
          <span class="text-2xl">🧾</span>
          <h2 class="mt-2 font-bold text-teal-950">Caisse & facturation</h2>
          <p class="mt-1 text-sm text-slate-600">Paiements, reçus PDF, statuts payé / en attente</p>
        </RouterLink>
        <RouterLink
          to="/messagerie"
          class="rounded-3xl border border-teal-100 bg-white p-5 shadow-sm transition hover:border-teal-300 hover:shadow-md"
        >
          <span class="text-2xl">💬</span>
          <h2 class="mt-2 font-bold text-teal-950">Messagerie</h2>
          <p class="mt-1 text-sm text-slate-600">Échanges avec les patients et l'équipe</p>
        </RouterLink>
        <RouterLink
          to="/rendez-vous"
          class="rounded-3xl border border-teal-100 bg-white p-5 shadow-sm transition hover:border-teal-300 hover:shadow-md"
        >
          <span class="text-2xl">📅</span>
          <h2 class="mt-2 font-bold text-teal-950">Planning complet</h2>
          <p class="mt-1 text-sm text-slate-600">Calendrier et gestion avancée</p>
        </RouterLink>
      </div>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-bold text-slate-900">Rendez-vous en attente de validation</h2>
            <p class="mt-1 text-sm text-slate-600">Les patients reçoivent une notification à chaque action.</p>
          </div>
          <span v-if="loading" class="text-sm text-slate-500">Chargement…</span>
        </div>

        <div v-if="!loading && pendingItems.length === 0" class="mt-6 rounded-2xl border border-dashed border-teal-200 bg-teal-50/50 px-6 py-10 text-center">
          <p class="text-lg font-semibold text-teal-900">Aucune demande en attente 💙</p>
          <p class="mt-2 text-sm text-slate-600">Les nouvelles demandes patient apparaîtront ici.</p>
        </div>

        <div v-else class="mt-4 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Date / heure</th>
                <th class="px-3 py-3 font-medium">Patient</th>
                <th class="px-3 py-3 font-medium">Médecin</th>
                <th class="px-3 py-3 font-medium">Motif</th>
                <th class="px-3 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="rdv in pendingItems" :key="rdv.id" class="hover:bg-teal-50/40">
                <td class="px-3 py-3 text-slate-800">{{ formatDateTime(rdv.date_heure) }}</td>
                <td class="px-3 py-3 text-slate-800">{{ rdv.patient_nom }}<br /><span class="text-xs text-slate-500">{{ rdv.numero_dossier }}</span></td>
                <td class="px-3 py-3 text-slate-800">{{ rdv.medecin_nom }}</td>
                <td class="px-3 py-3 text-slate-700">{{ rdv.motif }}</td>
                <td class="px-3 py-3">
                  <div class="flex flex-wrap gap-2">
                    <button
                      type="button"
                      class="rounded-full bg-emerald-100 px-3 py-1.5 text-xs font-bold text-emerald-900 transition hover:bg-emerald-200"
                      :disabled="busyId === rdv.id"
                      @click="validerRdv(rdv)"
                    >
                      Valider
                    </button>
                    <button
                      type="button"
                      class="rounded-full bg-sky-100 px-3 py-1.5 text-xs font-bold text-sky-900 transition hover:bg-sky-200"
                      @click="openPanel(rdv)"
                    >
                      Modifier
                    </button>
                    <button
                      type="button"
                      class="rounded-full bg-rose-100 px-3 py-1.5 text-xs font-bold text-rose-900 transition hover:bg-rose-200"
                      :disabled="busyId === rdv.id"
                      @click="annulerRdv(rdv)"
                    >
                      Annuler
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <RdvStaffPanel
      v-model:open="panelOpen"
      :rdv="selectedRdv"
      :medecins="medecins"
      :clinical-actions="false"
      @success="onPanelSuccess"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api, { getErrorMessage, unwrapList } from '../api/client.js'
import RdvStaffPanel from '../components/RdvStaffPanel.vue'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const loading = ref(true)
const busyId = ref(null)
const error = ref('')
const message = ref('')
const items = ref([])
const medecins = ref([])
const stats = ref({})
const panelOpen = ref(false)
const selectedRdv = ref(null)

const pendingItems = computed(() =>
  items.value
    .filter((r) => r.statut === 'planifie')
    .sort((a, b) => new Date(a.date_heure) - new Date(b.date_heure)),
)

function formatDateTime(iso) {
  try {
    return new Date(iso).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const [statsRes, listRes, medRes] = await Promise.all([
      api.get('/rendez-vous/stats/'),
      api.get('/rendez-vous/', { params: { statut: 'planifie' } }),
      api.get('/rendez-vous/medecins/'),
    ])
    stats.value = statsRes.data
    items.value = unwrapList(listRes.data)
    medecins.value = unwrapList(medRes.data)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function validerRdv(rdv) {
  busyId.value = rdv.id
  error.value = ''
  try {
    await api.post(`/rendez-vous/${rdv.id}/confirmer/`, { version: rdv.version })
    message.value = `Rendez-vous validé — ${rdv.patient_nom} a été notifié(e) ✅`
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    busyId.value = null
  }
}

async function annulerRdv(rdv) {
  const motif = window.prompt('Motif d\'annulation (envoyé au patient) :', 'Indisponibilité du créneau')
  if (motif === null) return
  busyId.value = rdv.id
  error.value = ''
  try {
    await api.post(`/rendez-vous/${rdv.id}/annuler/`, {
      version: rdv.version,
      motif_annulation: motif.trim() || 'Annulation secrétariat',
    })
    message.value = `Rendez-vous annulé — ${rdv.patient_nom} a été informé(e).`
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    busyId.value = null
  }
}

function openPanel(rdv) {
  selectedRdv.value = rdv
  panelOpen.value = true
}

function onPanelSuccess(msg) {
  message.value = msg
  loadAll()
}

onMounted(loadAll)
</script>
