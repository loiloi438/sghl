<template>
  <div class="space-y-6">
    <PatientPageHeader title="Mon profil" subtitle="Coordonnées utilisées pour les confirmations et rappels" :loading="loading" @refresh="load" />

    <div v-if="message" class="rounded-3xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
    <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>

    <div v-if="loading" class="rounded-3xl border border-slate-200 bg-white px-6 py-5 text-sm text-slate-600 shadow-sm">Chargement…</div>

    <form v-else-if="profil" class="space-y-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm" @submit.prevent="save">
      <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <h2 class="text-lg font-semibold text-slate-900">{{ profil.prenom }} {{ profil.nom }}</h2>
        <p class="mt-1 text-sm text-slate-500">Dossier {{ profil.numero_dossier }}</p>
        <p class="mt-2 text-sm text-slate-600">
          Né(e) le {{ profil.date_naissance }} · {{ profil.sexe === 'M' ? 'Homme' : profil.sexe === 'F' ? 'Femme' : profil.sexe }}
        </p>
      </div>

      <label class="grid gap-2 text-sm text-slate-700">
        <span>Adresse e-mail</span>
        <input v-model="form.email" type="email" required class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" />
      </label>
      <label class="grid gap-2 text-sm text-slate-700">
        <span>Téléphone</span>
        <input v-model="form.telephone" type="tel" required class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" />
      </label>
      <label class="grid gap-2 text-sm text-slate-700">
        <span>Adresse postale</span>
        <textarea v-model="form.adresse" rows="3" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" />
      </label>

      <button
        type="submit"
        class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60"
        :disabled="saving"
      >
        {{ saving ? 'Enregistrement…' : 'Enregistrer les modifications' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { getErrorMessage } from '../../api/client.js'
import PatientPageHeader from '../../components/patient/PatientPageHeader.vue'

const profil = ref(null)
const form = ref({ email: '', telephone: '', adresse: '' })
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const message = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/patient/profil/')
    profil.value = data
    form.value = {
      email: data.email || '',
      telephone: data.telephone || '',
      adresse: data.adresse || '',
    }
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    const { data } = await api.patch('/patient/profil/', form.value)
    profil.value = data
    message.value = 'Profil mis à jour.'
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
