<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <div class="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Patients</h1>
          <p class="mt-1 text-sm text-slate-600">Gestion des dossiers et identité patient</p>
        </div>
        <div class="flex flex-col gap-2 sm:items-end">
          <button
            v-if="auth.canPatientsWrite"
            class="rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700"
            type="button"
            @click="showForm = !showForm"
          >
            {{ showForm ? 'Annuler' : 'Nouveau patient' }}
          </button>
          <p v-else class="text-sm text-slate-500">Consultation seule — création réservée au personnel autorisé.</p>
        </div>
      </div>

      <div v-if="message" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
      <div v-if="error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</div>

      <div v-if="showForm && auth.canPatientsWrite" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Nouveau dossier patient</h2>
        <form class="mt-5 space-y-5" @submit.prevent="createPatient">
          <div>
            <p class="mb-4 text-sm font-medium text-slate-600">Identité et coordonnées</p>
            <div class="grid gap-4 md:grid-cols-2">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700" for="numero_dossier">N° dossier</label>
                <input
                  id="numero_dossier"
                  v-model="form.numero_dossier"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500"
                  placeholder="ex. P-2026-002"
                  required
                />
                <span class="mt-1 block text-xs text-slate-500">Identifiant unique du patient</span>
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700" for="sexe">Sexe</label>
                <select id="sexe" v-model="form.sexe" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500">
                  <option value="M">Masculin</option>
                  <option value="F">Féminin</option>
                </select>
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700" for="nom">Nom</label>
                <input id="nom" v-model="form.nom" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" required autocomplete="family-name" />
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700" for="prenom">Prénom</label>
                <input id="prenom" v-model="form.prenom" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" required autocomplete="given-name" />
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700" for="date_naissance">Date de naissance</label>
                <input id="date_naissance" v-model="form.date_naissance" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" type="date" required />
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700" for="telephone">Téléphone</label>
                <input id="telephone" v-model="form.telephone" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" type="tel" placeholder="+242 …" />
              </div>
            </div>
          </div>
          <label class="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-3 text-sm text-slate-700">
            <input v-model="form.consentement_donnees" class="mt-0.5 h-4 w-4 rounded border-slate-300" type="checkbox" />
            <span>Le patient a donné son consentement pour le traitement des données personnelles (RGPD).</span>
          </label>
          <div class="flex flex-col gap-3 sm:flex-row">
            <button class="rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700" type="submit" :disabled="saving">
              {{ saving ? 'Enregistrement…' : 'Enregistrer le dossier' }}
            </button>
            <button class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" type="button" @click="showForm = false">Annuler</button>
          </div>
        </form>
      </div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <input
            v-model="search"
            class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500 md:max-w-md"
            type="search"
            placeholder="Rechercher par nom ou n° dossier…"
            @input="debouncedLoad"
          />
        </div>
        <div v-if="loading" class="text-sm text-slate-500">Chargement…</div>
        <div v-else-if="patients.length === 0" class="text-sm text-slate-500">Aucun patient trouvé.</div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Dossier</th>
                <th class="px-3 py-3 font-medium">Nom</th>
                <th class="px-3 py-3 font-medium">Naissance</th>
                <th class="px-3 py-3 font-medium">Sexe</th>
                <th class="px-3 py-3 font-medium">Téléphone</th>
                <th class="px-3 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="p in patients" :key="p.id" class="hover:bg-slate-50">
                <td class="px-3 py-3">
                  <RouterLink :to="{ name: 'patient-detail', params: { id: p.id } }" class="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 transition hover:bg-emerald-100">
                    {{ p.numero_dossier }}
                  </RouterLink>
                </td>
                <td class="px-3 py-3">
                  <RouterLink :to="{ name: 'patient-detail', params: { id: p.id } }" class="font-semibold text-slate-900 transition hover:text-blue-600">
                    {{ p.prenom }} {{ p.nom }}
                  </RouterLink>
                </td>
                <td class="px-3 py-3 text-slate-700">{{ p.date_naissance }}</td>
                <td class="px-3 py-3 text-slate-700">{{ p.sexe === 'M' ? 'M' : 'F' }}</td>
                <td class="px-3 py-3 text-slate-700">{{ p.telephone || '—' }}</td>
                <td class="px-3 py-3">
                  <RouterLink
                    :to="{ name: 'patient-detail', params: { id: p.id } }"
                    class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
                  >
                    Voir dossier
                  </RouterLink>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api, { getErrorMessage, unwrapList } from '../api/client.js'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()

const patients = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const message = ref('')
const search = ref('')
const showForm = ref(false)
let searchTimer

const form = reactive({
  numero_dossier: '',
  nom: '',
  prenom: '',
  date_naissance: '',
  sexe: 'M',
  telephone: '',
  consentement_donnees: false,
})

function debouncedLoad() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(load, 300)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = search.value ? `?search=${encodeURIComponent(search.value)}` : ''
    const { data } = await api.get(`/patients/${params}`)
    patients.value = unwrapList(data)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function createPatient() {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    await api.post('/patients/', form)
    message.value = 'Patient enregistré.'
    showForm.value = false
    Object.assign(form, {
      numero_dossier: '',
      nom: '',
      prenom: '',
      date_naissance: '',
      sexe: 'M',
      telephone: '',
      consentement_donnees: false,
    })
    await load()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
