<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto max-w-7xl space-y-6">
      <header class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Téléconsultation</h1>
            <p class="mt-1 text-sm text-slate-600">Consultations médicales à distance par vidéo</p>
          </div>
          <button class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-100" type="button" @click="loadAll">Actualiser</button>
        </div>
      </header>

      <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>

      <div class="grid gap-4 md:grid-cols-3">
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Consultations ce mois</span>
          <div class="mt-3 text-3xl font-semibold text-slate-900">{{ stats.consultations_ce_mois }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">En cours</span>
          <div class="mt-3 text-3xl font-semibold text-emerald-600">{{ stats.en_cours }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Patients satisfaits</span>
          <div class="mt-3 text-3xl font-semibold text-slate-900">{{ stats.satisfaction_rate }}%</div>
        </article>
      </div>

      <div class="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
        <nav class="flex flex-wrap gap-2">
          <button type="button" @click="setTab('scheduled')" :class="tabClass(activeTab === 'scheduled')">Programmées</button>
          <button type="button" @click="setTab('completed')" :class="tabClass(activeTab === 'completed')">Terminées</button>
          <button type="button" @click="setTab('cancelled')" :class="tabClass(activeTab === 'cancelled')">Annulées</button>
        </nav>
      </div>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div v-if="loading" class="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">Chargement…</div>
        <div v-else-if="consultations.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">Aucune consultation dans cette catégorie.</div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200">
            <thead class="bg-slate-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Patient</th>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Médecin</th>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Date & Heure</th>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Durée</th>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Statut</th>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 bg-white">
              <tr v-for="consultation in consultations" :key="consultation.id" class="hover:bg-slate-50">
                <td class="whitespace-nowrap px-4 py-4 text-sm font-semibold text-slate-900">{{ consultation.patientName }}</td>
                <td class="whitespace-nowrap px-4 py-4 text-sm text-slate-700">Dr {{ consultation.doctorName }}</td>
                <td class="whitespace-nowrap px-4 py-4 text-sm text-slate-700">{{ consultation.dateTime }}</td>
                <td class="whitespace-nowrap px-4 py-4 text-sm text-slate-700">{{ consultation.duration }} min</td>
                <td class="whitespace-nowrap px-4 py-4">
                  <span :class="statusBadgeClass(consultation.status)">{{ statusLabel(consultation.status) }}</span>
                </td>
                <td class="whitespace-nowrap px-4 py-4">
                  <button v-if="consultation.status === 'scheduled'" @click="joinConsultation(consultation)" class="inline-flex rounded-2xl bg-sky-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-sky-700">Rejoindre</button>
                  <button v-else @click="viewRecording(consultation)" class="inline-flex rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">Dossier</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { getErrorMessage, unwrapList } from '../api/client.js'

const consultations = ref([])
const stats = ref({ consultations_ce_mois: 0, en_cours: 0, satisfaction_rate: 0 })
const loading = ref(true)
const error = ref('')
const activeTab = ref('scheduled')

const statusLabel = (status) => ({
  scheduled: 'Programmée',
  completed: 'Terminée',
  cancelled: 'Annulée',
  in_progress: 'En cours',
}[status] || status)

const statusBadgeClass = (status) => ({
  scheduled: 'rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-amber-700',
  completed: 'rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700',
  cancelled: 'rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-700',
  in_progress: 'rounded-full bg-sky-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-sky-700',
}[status] || 'rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-700')

const tabClass = (active) => (
  active
    ? 'rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm'
    : 'rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50'
)

async function loadStats() {
  const { data } = await api.get('/teleconsultation/stats/')
  stats.value = data
}

async function loadConsultations() {
  const { data } = await api.get(`/teleconsultation/?status=${activeTab.value}`)
  consultations.value = unwrapList(data)
}

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([loadStats(), loadConsultations()])
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

function setTab(tab) {
  activeTab.value = tab
  loadConsultations()
}

async function joinConsultation(consultation) {
  error.value = ''
  try {
    let url = consultation.lien_visio
    if (!url) {
      const { data } = await api.post(`/teleconsultation/${consultation.id}/lien/`)
      url = data.lien_visio
    }
    window.open(url, '_blank', 'noopener,noreferrer')
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

function viewRecording(consultation) {
  alert(`Consultation ${consultation.patientName} — ${statusLabel(consultation.status)}\nLe dossier patient reste accessible depuis le module Patients.`)
}

onMounted(loadAll)
</script>
