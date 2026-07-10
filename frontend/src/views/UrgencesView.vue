<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto max-w-7xl space-y-6">
      <header class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Urgences</h1>
            <p class="mt-1 text-sm text-slate-600">Accueil, triage et flux de prise en charge</p>
          </div>
          <div class="flex gap-2">
            <button class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-100" type="button" @click="loadAll">Actualiser</button>
            <button class="rounded-2xl bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-sky-700" type="button" @click="showArrivalForm = !showArrivalForm">+ Nouvel arrivant</button>
          </div>
        </div>
      </header>

      <div v-if="message" class="rounded-3xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
      <div v-if="error" class="rounded-3xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</div>

      <form v-if="showArrivalForm" class="grid gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-2" @submit.prevent="admitPatient">
        <h2 class="md:col-span-2 text-lg font-semibold text-slate-900">Enregistrer un arrivant</h2>
        <div class="md:col-span-2 flex flex-wrap gap-2">
          <button type="button" class="rounded-2xl px-4 py-2 text-sm font-semibold transition" :class="arrivalMode === 'existing' ? 'bg-sky-600 text-white' : 'border border-slate-200 text-slate-700'" @click="arrivalMode = 'existing'">Patient existant</button>
          <button type="button" class="rounded-2xl px-4 py-2 text-sm font-semibold transition" :class="arrivalMode === 'new' ? 'bg-sky-600 text-white' : 'border border-slate-200 text-slate-700'" @click="arrivalMode = 'new'">Nouvel arrivant</button>
        </div>
        <template v-if="arrivalMode === 'existing'">
          <select v-model="arrivalForm.patient_id" required class="md:col-span-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-sky-500">
            <option value="">— Sélectionner un patient —</option>
            <option v-for="p in patientsList" :key="p.id" :value="p.id">{{ p.numero_dossier }} — {{ p.prenom }} {{ p.nom }}</option>
          </select>
        </template>
        <template v-else>
          <input v-model="arrivalForm.nom_libre" required placeholder="Nom du patient" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-sky-500" />
          <input v-model.number="arrivalForm.age" type="number" min="0" placeholder="Âge" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-sky-500" />
          <select v-model="arrivalForm.sexe" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-sky-500">
            <option value="">Sexe</option>
            <option value="M">Masculin</option>
            <option value="F">Féminin</option>
          </select>
        </template>
        <select v-model="arrivalForm.niveau_triage" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-sky-500">
          <option value="red">Rouge — Urgence majeure</option>
          <option value="orange">Orange — Urgent</option>
          <option value="green">Vert — Peu urgent</option>
          <option value="blue">Bleu — Non urgent</option>
        </select>
        <textarea v-model="arrivalForm.motif" required rows="2" placeholder="Motif de consultation" class="md:col-span-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-sky-500"></textarea>
        <div class="md:col-span-2 flex gap-2">
          <button type="submit" class="rounded-2xl bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-sky-700" :disabled="saving">Enregistrer</button>
          <button type="button" class="rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50" @click="showArrivalForm = false">Annuler</button>
        </div>
      </form>

      <div class="grid gap-4 md:grid-cols-3">
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">En attente de triage</span>
          <div class="mt-3 text-3xl font-semibold text-rose-600">{{ stats.waiting_triage }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Patients en salle</span>
          <div class="mt-3 text-3xl font-semibold text-amber-600">{{ stats.in_treatment }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Temps moyen attente</span>
          <div class="mt-3 text-3xl font-semibold text-slate-900">{{ stats.avg_wait_minutes }} min</div>
        </article>
      </div>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="grid gap-4 lg:grid-cols-[1.4fr_0.6fr] lg:items-end">
          <input v-model="search" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100" type="search" placeholder="Rechercher un patient…" @input="debouncedLoad" />
          <select v-model="triageFilter" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100" @change="loadPassages">
            <option value="">Tous les niveaux</option>
            <option value="red">Urgence majeure (rouge)</option>
            <option value="orange">Urgent (orange)</option>
            <option value="green">Peu urgent (vert)</option>
            <option value="blue">Non urgent (bleu)</option>
          </select>
        </div>

        <div v-if="loading" class="mt-6 rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">Chargement…</div>
        <div v-else-if="patients.length === 0" class="mt-6 rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">Aucun patient en attente.</div>

        <div v-else class="mt-6 grid gap-4 lg:grid-cols-2">
          <article v-for="patient in patients" :key="patient.id" :class="['rounded-3xl border p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md', triagePanelClass(patient.triage)]">
            <div class="flex items-center justify-between gap-3">
              <span :class="triageBadgeClass(patient.triage)">{{ patient.triage_label || triageLabel(patient.triage) }}</span>
              <span class="text-xs text-slate-500">{{ patient.arrivalTime }}</span>
            </div>
            <h3 class="mt-4 text-lg font-semibold text-slate-900">{{ patient.name }}</h3>
            <p class="mt-2 text-sm text-slate-600">{{ patient.age ?? '—' }} ans — {{ patient.gender }}</p>
            <p class="mt-3 text-sm leading-6 text-slate-700">{{ patient.complaint }}</p>
            <p class="mt-2 text-xs uppercase tracking-wide text-slate-500">Statut : {{ patient.statut }}</p>
            <div class="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center">
              <button class="w-full rounded-2xl bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-sky-700 sm:w-auto" :disabled="saving" @click="startTriage(patient)">Débuter triage</button>
              <button class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 sm:w-auto" :disabled="saving" @click="moveToRoom(patient)">Salle de soin</button>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { getErrorMessage, unwrapList } from '../api/client.js'

const patients = ref([])
const patientsList = ref([])
const stats = ref({ waiting_triage: 0, in_treatment: 0, avg_wait_minutes: 0 })
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const message = ref('')
const search = ref('')
const triageFilter = ref('')
const showArrivalForm = ref(false)
const arrivalMode = ref('existing')
const arrivalForm = ref({ patient_id: '', nom_libre: '', age: null, sexe: '', motif: '', niveau_triage: 'orange' })

let debounceTimer = null

function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadPassages, 300)
}

const triageLabel = (triage) => ({
  red: 'Urgence majeure',
  orange: 'Urgent',
  green: 'Peu urgent',
  blue: 'Non urgent',
}[triage] || triage)

const triageBadgeClass = (triage) => {
  const classes = {
    red: 'rounded-full bg-rose-600 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-white',
    orange: 'rounded-full bg-amber-500 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-900',
    green: 'rounded-full bg-emerald-500 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-white',
    blue: 'rounded-full bg-sky-500 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-white',
  }
  return classes[triage] || 'rounded-full bg-slate-200 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-700'
}

const triagePanelClass = (triage) => {
  const classes = {
    red: 'border-rose-300/70 bg-rose-50',
    orange: 'border-amber-300/70 bg-amber-50',
    green: 'border-emerald-300/70 bg-emerald-50',
    blue: 'border-sky-300/70 bg-sky-50',
  }
  return classes[triage] || 'border-slate-200 bg-slate-50'
}

async function loadStats() {
  const { data } = await api.get('/urgences/stats/')
  stats.value = data
}

async function loadPassages() {
  const params = new URLSearchParams()
  if (search.value.trim()) params.set('search', search.value.trim())
  if (triageFilter.value) params.set('triage', triageFilter.value)
  const qs = params.toString()
  const { data } = await api.get(`/urgences/passages/${qs ? `?${qs}` : ''}`)
  patients.value = unwrapList(data)
}

async function loadPatients() {
  const { data } = await api.get('/patients/')
  patientsList.value = unwrapList(data)
}

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([loadStats(), loadPassages(), loadPatients()])
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function admitPatient() {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    const body = {
      motif: arrivalForm.value.motif,
      niveau_triage: arrivalForm.value.niveau_triage,
    }
    if (arrivalMode.value === 'existing') {
      body.patient_id = arrivalForm.value.patient_id
    } else {
      body.nom_libre = arrivalForm.value.nom_libre
      body.age = arrivalForm.value.age
      body.sexe = arrivalForm.value.sexe
    }
    await api.post('/urgences/passages/', body)
    message.value = 'Arrivant enregistré.'
    arrivalForm.value = { patient_id: '', nom_libre: '', age: null, sexe: '', motif: '', niveau_triage: 'orange' }
    showArrivalForm.value = false
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

async function startTriage(patient) {
  saving.value = true
  error.value = ''
  try {
    await api.post(`/urgences/passages/${patient.id}/triage/`, { version: patient.version })
    message.value = `Triage démarré pour ${patient.name}.`
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

async function moveToRoom(patient) {
  saving.value = true
  error.value = ''
  try {
    await api.post(`/urgences/passages/${patient.id}/classer/`, {
      version: patient.version,
      niveau_triage: patient.triage,
    })
    message.value = `${patient.name} orienté en salle de soins.`
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

onMounted(loadAll)
</script>
