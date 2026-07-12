<template>
  <div class="hc-page">
    <PatientPageHeader
      title="Mes rendez-vous"
      subtitle="Planifiez vos consultations — confirmations et rappels par e-mail 💙"
      module="calendar"
      :loading="loading"
      @refresh="load"
    />

    <div v-if="message" class="hc-alert hc-alert--success">{{ message }}</div>
    <div v-if="error" class="hc-alert hc-alert--error">{{ error }}</div>

    <section class="hc-card hc-card-padded">
      <h2 class="font-bold text-teal-900" style="font-family: Poppins, sans-serif">Nouveau rendez-vous</h2>
      <p class="mt-2 text-sm text-slate-600">
        Renseignez vos coordonnées pour recevoir les confirmations, rappels et alertes.
      </p>

      <form class="mt-6 grid gap-6" @submit.prevent="createRdv">
        <fieldset class="rounded-2xl border border-emerald-100 bg-emerald-50/40 p-5">
          <legend class="px-2 text-sm font-bold text-teal-800">Vos coordonnées</legend>
          <div class="mt-4 grid gap-4 sm:grid-cols-2">
            <label class="grid gap-2 text-sm text-slate-700">
              <span class="font-semibold">Adresse e-mail <span class="text-rose-500">*</span></span>
              <input
                id="email"
                v-model="form.email"
                type="email"
                autocomplete="email"
                placeholder="vous@exemple.com"
                required
                class="hc-input a11y-touch"
              />
            </label>
            <label class="grid gap-2 text-sm text-slate-700">
              <span class="font-semibold">Confirmer l'e-mail <span class="text-rose-500">*</span></span>
              <input
                id="email-confirm"
                v-model="form.email_confirm"
                type="email"
                autocomplete="email"
                placeholder="Retapez votre e-mail"
                required
                class="hc-input a11y-touch"
              />
            </label>
            <label class="grid gap-2 text-sm text-slate-700">
              <span class="font-semibold">Téléphone <span class="text-rose-500">*</span></span>
              <input
                id="telephone"
                v-model="form.telephone"
                type="tel"
                autocomplete="tel"
                placeholder="+242 06 000 00 00"
                required
                class="hc-input a11y-touch"
              />
            </label>
            <label class="sm:col-span-2 grid gap-2 text-sm text-slate-700">
              <span class="font-semibold">Adresse postale</span>
              <textarea
                id="adresse"
                v-model="form.adresse"
                rows="2"
                placeholder="Rue, quartier, ville"
                class="hc-input a11y-touch"
              />
            </label>
          </div>
        </fieldset>

        <fieldset class="rounded-2xl border border-sky-100 bg-sky-50/40 p-5">
          <legend class="px-2 text-sm font-bold text-sky-800">Consultation</legend>
          <div class="mt-4 grid gap-4 sm:grid-cols-2">
            <label class="grid gap-2 text-sm text-slate-700">
              <span class="font-semibold">Médecin <span class="text-rose-500">*</span></span>
              <select id="medecin" v-model="form.medecin_id" required class="hc-input a11y-touch">
                <option value="">— Choisir —</option>
                <option v-for="m in medecins" :key="m.id" :value="String(m.id)">{{ m.nom }}</option>
              </select>
            </label>
            <label class="grid gap-2 text-sm text-slate-700">
              <span class="font-semibold">Date et heure <span class="text-rose-500">*</span></span>
              <input
                id="date-heure"
                v-model="form.date_heure"
                type="datetime-local"
                required
                class="hc-input a11y-touch"
              />
            </label>
            <label class="grid gap-2 text-sm text-slate-700">
              <span class="font-semibold">Type de consultation</span>
              <select id="type-consultation" v-model="form.type_consultation" class="hc-input a11y-touch">
                <option value="presentiel">Présentiel</option>
                <option value="teleconsultation">Téléconsultation (visio)</option>
              </select>
            </label>
            <label class="grid gap-2 text-sm text-slate-700">
              <span class="font-semibold">Durée (minutes)</span>
              <input
                id="duree"
                v-model.number="form.duree_minutes"
                type="number"
                min="15"
                max="120"
                step="5"
                class="hc-input a11y-touch"
              />
            </label>
            <label class="sm:col-span-2 grid gap-2 text-sm text-slate-700">
              <span class="font-semibold">Motif de consultation <span class="text-rose-500">*</span></span>
              <textarea
                id="motif"
                v-model="form.motif"
                rows="2"
                required
                placeholder="Ex. Consultation générale, suivi…"
                class="hc-input a11y-touch"
              />
            </label>
          </div>
        </fieldset>

        <div class="flex justify-end">
          <button type="submit" class="hc-btn-rdv a11y-touch" :disabled="saving">
            {{ saving ? 'Envoi…' : '📅 Demander le rendez-vous' }}
          </button>
        </div>
      </form>
    </section>

    <section class="hc-card hc-card-padded">
      <div class="flex items-center justify-between gap-4">
        <h2 class="font-bold text-teal-900" style="font-family: Poppins, sans-serif">Historique</h2>
        <span v-if="loading" class="text-sm text-slate-500">Chargement…</span>
      </div>

      <PatientEmptyState
        v-if="!loading && !items.length"
        icon="📅"
        title="Aucun rendez-vous pour l'instant"
        text="Prenez rendez-vous en quelques clics — nous vous accompagnons à chaque étape 💙"
        class="mt-4"
      />

      <div v-else class="mt-4 space-y-3">
        <article v-for="rdv in items" :key="rdv.id" class="hc-list-item">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div class="flex gap-3">
              <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-sky-100 text-xl">👨‍⚕️</span>
              <div>
                <h3 class="font-bold text-slate-900">{{ rdv.medecin_nom }}</h3>
                <p class="mt-1 text-sm text-slate-600">{{ formatDateTime(rdv.date_heure) }}</p>
                <p class="mt-1 text-sm text-slate-500">{{ rdv.motif }}</p>
              </div>
            </div>
            <div class="flex flex-wrap gap-2">
              <span
                class="hc-badge"
                :class="rdv.type_consultation === 'teleconsultation' ? 'hc-badge--done' : 'hc-badge--ok'"
              >
                {{ typeConsultationLabel(rdv.type_consultation) }}
              </span>
              <span
                class="hc-badge"
                :class="rdvStatutBadgeClass(rdv.statut)"
              >{{ statutLabel(rdv.statut) }}</span>
            </div>
          </div>
          <div class="mt-4 flex flex-wrap gap-2">
            <a
              v-if="rdv.lien_visio"
              :href="rdv.lien_visio"
              target="_blank"
              rel="noopener noreferrer"
              class="hc-btn-secondary"
            >
              🎥 Rejoindre la visio
            </a>
            <button
              v-if="peutAnnuler(rdv.statut)"
              type="button"
              class="hc-btn-secondary !border-rose-200 !text-rose-700"
              :disabled="saving"
              @click="requestAnnuler(rdv)"
            >
              Annuler
            </button>
          </div>
        </article>
      </div>
    </section>
  </div>

  <PromptDialog
    :open="cancelDialog.open"
    title="Annuler le rendez-vous"
    message="Indiquez un motif d'annulation (optionnel)."
    v-model="cancelDialog.motif"
    input-label="Motif"
    placeholder="Annulation par le patient"
    confirm-label="Confirmer l'annulation"
    :loading="saving"
    @confirm="confirmAnnuler"
    @cancel="cancelDialog.open = false"
  />
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import PromptDialog from '../../components/PromptDialog.vue'
import PatientEmptyState from '../../components/patient/PatientEmptyState.vue'
import PatientPageHeader from '../../components/patient/PatientPageHeader.vue'
import api from '../../api/client.js'
import { showToast } from '../../composables/useToast.js'
import { rdvStatutLabel, typeConsultationLabel } from '../../composables/usePatientPortal.js'

const items = ref([])
const medecins = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const message = ref(null)
const cancelDialog = ref({ open: false, motif: 'Annulation par le patient', rdv: null })

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

function rdvStatutBadgeClass(statut) {
  if (statut === 'confirme') return 'hc-badge--ok'
  if (statut === 'annule') return 'hc-badge--alert'
  if (statut === 'planifie') return 'hc-badge--pending'
  return 'hc-badge--done'
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
      ? 'Rendez-vous planifié ✅ Un lien visio sera disponible après validation.'
      : 'Rendez-vous planifié ✅ Le secrétariat vous confirmera très bientôt.'
    showToast(message.value, 'success')
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

function requestAnnuler(rdv) {
  cancelDialog.value = {
    open: true,
    motif: 'Annulation par le patient',
    rdv,
  }
}

async function confirmAnnuler(motif) {
  const rdv = cancelDialog.value.rdv
  if (!rdv) return

  saving.value = true
  error.value = null
  try {
    await api.post(`/patient/rendez-vous/${rdv.id}/annuler/`, {
      version: rdv.version,
      motif_annulation: motif || 'Annulation par le patient',
    })
    cancelDialog.value.open = false
    message.value = 'Rendez-vous annulé — un e-mail de confirmation vous sera envoyé 💙'
    showToast('Rendez-vous annulé.', 'success')
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

<style scoped>
.hc-input {
  width: 100%;
  border-radius: 1rem;
  border: 1px solid #a7f3d0;
  background: rgba(255, 255, 255, 0.9);
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #134e4a;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.hc-input:focus {
  border-color: #2dd4bf;
  box-shadow: 0 0 0 3px rgba(45, 212, 191, 0.25);
}
</style>
