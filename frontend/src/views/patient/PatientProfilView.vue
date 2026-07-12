<template>
  <div class="hc-page">
    <PatientPageHeader
      title="Mon profil"
      subtitle="Vos coordonnées pour les confirmations, rappels et soins 💙"
      module="profile"
      :loading="loading"
      @refresh="load"
    />

    <div v-if="message" class="hc-alert hc-alert--success">{{ message }}</div>
    <div v-if="error" class="hc-alert hc-alert--error">{{ error }}</div>
    <div v-if="loading" class="hc-loading">Chargement de votre profil…</div>

    <form v-else-if="profil" class="hc-card hc-card-padded space-y-6" @submit.prevent="save">
      <div class="rounded-2xl border border-emerald-100 bg-emerald-50/50 p-5">
        <h2 class="text-xl font-bold text-teal-950" style="font-family: Poppins, sans-serif">
          {{ profil.prenom }} {{ profil.nom }}
        </h2>
        <p class="mt-1 text-sm text-slate-500">Dossier {{ profil.numero_dossier }}</p>
        <p class="mt-2 text-sm text-slate-600">
          Né(e) le {{ profil.date_naissance }} ·
          {{ profil.sexe === 'M' ? 'Homme' : profil.sexe === 'F' ? 'Femme' : profil.sexe }}
        </p>
      </div>

      <label class="grid gap-2 text-sm text-slate-700">
        <span class="font-semibold">Adresse e-mail</span>
        <input v-model="form.email" type="email" required class="hc-input a11y-touch" />
      </label>
      <label class="grid gap-2 text-sm text-slate-700">
        <span class="font-semibold">Téléphone</span>
        <input v-model="form.telephone" type="tel" required class="hc-input a11y-touch" />
      </label>
      <label class="grid gap-2 text-sm text-slate-700">
        <span class="font-semibold">Adresse postale</span>
        <textarea v-model="form.adresse" rows="3" class="hc-input a11y-touch" />
      </label>

      <button type="submit" class="hc-btn-rdv a11y-touch" :disabled="saving">
        {{ saving ? 'Enregistrement…' : '💾 Enregistrer les modifications' }}
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
    message.value = 'Profil mis à jour — merci de veiller à vos informations 💙'
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
