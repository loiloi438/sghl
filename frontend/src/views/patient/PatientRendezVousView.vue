<template>
  <div class="space-y-6">
      <div class="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Mes rendez-vous</h1>
          <p class="mt-1 text-sm text-slate-600">Demande en ligne — confirmations et rappels par e-mail</p>
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

      <div v-if="message" class="rounded-3xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700 shadow-sm">{{ message }}</div>
      <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 shadow-sm">{{ error }}</div>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Nouveau rendez-vous</h2>
        <p class="mt-2 text-sm text-slate-600">
          Renseignez vos coordonnées pour recevoir les confirmations, rappels et alertes (modification, annulation).
        </p>

        <form @submit.prevent="createRdv" class="mt-6 grid gap-6">
          <fieldset class="grid gap-6 rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <legend class="px-2 text-sm font-semibold text-slate-900">Vos coordonnées</legend>
            <div class="grid gap-4 sm:grid-cols-2">
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Adresse e-mail <span class="text-rose-600">*</span></span>
                <input
                  id="email"
                  v-model="form.email"
                  type="email"
                  autocomplete="email"
                  placeholder="vous@exemple.com"
                  required
                  class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                />
              </label>
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Confirmer l'e-mail <span class="text-rose-600">*</span></span>
                <input
                  id="email-confirm"
                  v-model="form.email_confirm"
                  type="email"
                  autocomplete="email"
                  placeholder="Retapez votre e-mail"
                  required
                  class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                />
              </label>
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Téléphone <span class="text-rose-600">*</span></span>
                <input
                  id="telephone"
                  v-model="form.telephone"
                  type="tel"
                  autocomplete="tel"
                  placeholder="+242 06 000 00 00"
                  required
                  class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                />
              </label>
              <label class="sm:col-span-2 grid gap-2 text-sm text-slate-700">
                <span>Adresse postale</span>
                <textarea
                  id="adresse"
                  v-model="form.adresse"
                  rows="2"
                  placeholder="Rue, quartier, ville"
                  class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                />
              </label>
            </div>
          </fieldset>

          <fieldset class="grid gap-6 rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <legend class="px-2 text-sm font-semibold text-slate-900">Consultation</legend>
            <div class="grid gap-4 sm:grid-cols-2">
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Médecin <span class="text-rose-600">*</span></span>
                <select
                  id="medecin"
                  v-model="form.medecin_id"
                  required
                  class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                >
                  <option value="">— Choisir —</option>
                  <option v-for="m in medecins" :key="m.id" :value="String(m.id)">{{ m.nom }}</option>
                </select>
              </label>
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Date et heure <span class="text-rose-600">*</span></span>
                <input
                  id="date-heure"
                  v-model="form.date_heure"
                  type="datetime-local"
                  required
                  class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                />
              </label>
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Type de consultation</span>
                <select
                  id="type-consultation"
                  v-model="form.type_consultation"
                  class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                >
                  <option value="presentiel">Présentiel</option>
                  <option value="teleconsultation">Téléconsultation (visio)</option>
                </select>
              </label>
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Durée (minutes)</span>
                <input
                  id="duree"
                  v-model.number="form.duree_minutes"
                  type="number"
                  min="15"
                  max="120"
                  step="5"
                  class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                />
              </label>
              <label class="sm:col-span-2 grid gap-2 text-sm text-slate-700">
                <span>Motif de consultation <span class="text-rose-600">*</span></span>
                <textarea
                  id="motif"
                  v-model="form.motif"
                  rows="2"
                  required
                  placeholder="Ex. Consultation générale, suivi…"
                  class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                />
              </label>
            </div>
          </fieldset>

          <div class="flex justify-end">
            <button
              class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              type="submit"
              :disabled="saving"
            >
              {{ saving ? 'Envoi…' : 'Demander le rendez-vous' }}
            </button>
          </div>
        </form>
      </section>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex items-center justify-between gap-4">
          <h2 class="text-lg font-semibold text-slate-900">Historique</h2>
          <span v-if="loading" class="text-sm text-slate-600">Chargement…</span>
        </div>
        <div v-if="!loading && !items.length" class="mt-4 text-sm text-slate-600">Aucun rendez-vous pour le moment.</div>
        <div v-else class="mt-4 overflow-hidden rounded-3xl border border-slate-200">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-slate-600">
              <tr>
                <th class="px-4 py-3 text-left font-medium">Date</th>
                <th class="px-4 py-3 text-left font-medium">Médecin</th>
                <th class="px-4 py-3 text-left font-medium">Motif</th>
                <th class="px-4 py-3 text-left font-medium">Type</th>
                <th class="px-4 py-3 text-left font-medium">Statut</th>
                <th class="px-4 py-3 text-left font-medium"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 bg-white">
              <tr v-for="rdv in items" :key="rdv.id" class="hover:bg-slate-50">
                <td class="px-4 py-4 text-slate-700">{{ formatDateTime(rdv.date_heure) }}</td>
                <td class="px-4 py-4 text-slate-700">{{ rdv.medecin_nom }}</td>
                <td class="px-4 py-4 text-slate-700">{{ rdv.motif }}</td>
                <td class="px-4 py-4 text-slate-700">
                  <span
                    class="inline-flex rounded-full px-3 py-1 text-xs font-semibold"
                    :class="rdv.type_consultation === 'teleconsultation' ? 'bg-sky-100 text-sky-700' : 'bg-slate-100 text-slate-600'"
                  >
                    {{ typeConsultationLabel(rdv.type_consultation) }}
                  </span>
                  <a
                    v-if="rdv.lien_visio"
                    :href="rdv.lien_visio"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="ml-2 text-xs font-semibold text-blue-600 hover:text-blue-700"
                  >
                    Rejoindre
                  </a>
                </td>
                <td class="px-4 py-4">
                  <span class="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">{{ statutLabel(rdv.statut) }}</span>
                </td>
                <td class="px-4 py-4">
                  <button
                    v-if="peutAnnuler(rdv.statut)"
                    type="button"
                    class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                    :disabled="saving"
                    @click="annuler(rdv)"
                  >
                    Annuler
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import api from '../../api/client.js'
import { rdvStatutLabel, typeConsultationLabel } from '../../composables/usePatientPortal.js'

const items = ref([])
const medecins = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const message = ref(null)

const form = reactive({
  email: '',
  email_confirm: '',
  telephone: '',
  adresse: '',
  medecin_id: '',
  date_heure: '',
  duree_minutes: 30,
  motif: '',
  type_consultation: 'presentiel',
})

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

function statutLabel(s) {
  return rdvStatutLabel(s)
}

function peutAnnuler(statut) {
  return statut === 'planifie' || statut === 'confirme'
}

function toLocalDatetimeInput(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function loadProfil() {
  try {
    const { data } = await api.get('/patient/profil/')
    form.email = data.email || ''
    form.email_confirm = data.email || ''
    form.telephone = data.telephone || ''
    form.adresse = data.adresse || ''
  } catch {
    /* profil optionnel au chargement */
  }
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const [rdvRes, medRes] = await Promise.all([
      api.get('/patient/rendez-vous/'),
      api.get('/patient/rendez-vous/medecins/'),
    ])
    items.value = rdvRes.data.items ?? rdvRes.data ?? []
    medecins.value = medRes.data.items ?? medRes.data ?? []
  } catch (e) {
    error.value = e.response?.data?.detail || 'Impossible de charger les rendez-vous.'
  } finally {
    loading.value = false
  }
}

async function createRdv() {
  message.value = null
  error.value = null

  if (form.email.trim().toLowerCase() !== form.email_confirm.trim().toLowerCase()) {
    error.value = 'Les adresses e-mail ne correspondent pas.'
    return
  }

  if (!form.medecin_id || !form.date_heure || !form.motif.trim()) {
    error.value = 'Complétez le médecin, la date et le motif.'
    return
  }

  saving.value = true
  try {
    const dateHeure = new Date(form.date_heure)
    await api.post('/patient/rendez-vous/', {
      medecin_id: Number(form.medecin_id),
      date_heure: dateHeure.toISOString(),
      motif: form.motif.trim(),
      duree_minutes: form.duree_minutes,
      type_consultation: form.type_consultation,
      email: form.email.trim(),
      email_confirm: form.email_confirm.trim(),
      telephone: form.telephone.trim(),
      adresse: form.adresse.trim(),
    })
    message.value = form.type_consultation === 'teleconsultation'
      ? 'Demande enregistrée. Un lien visio sera disponible après confirmation.'
      : 'Demande enregistrée. Vous recevrez un e-mail de confirmation si votre adresse est valide.'
    form.motif = ''
    form.medecin_id = ''
    form.date_heure = ''
    await load()
    await loadProfil()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Impossible de créer le rendez-vous.'
  } finally {
    saving.value = false
  }
}

async function annuler(rdv) {
  const motif = window.prompt('Motif d\'annulation (optionnel) :', 'Annulation par le patient')
  if (motif === null) return

  saving.value = true
  error.value = null
  try {
    await api.post(`/patient/rendez-vous/${rdv.id}/annuler/`, {
      version: rdv.version,
      motif_annulation: motif,
    })
    message.value = 'Rendez-vous annulé. Un e-mail de confirmation vous sera envoyé.'
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Annulation impossible.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const now = new Date()
  now.setDate(now.getDate() + 1)
  now.setMinutes(0)
  form.date_heure = toLocalDatetimeInput(now.toISOString())
  await loadProfil()
  await load()
})
</script>
