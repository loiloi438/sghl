<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <RouterLink
        to="/patients"
        class="inline-flex w-fit items-center gap-2 text-sm font-medium text-slate-600 transition hover:text-blue-600"
      >
        ← Retour à la liste
      </RouterLink>

      <div v-if="loading" class="rounded-3xl border border-slate-200 bg-white p-8 text-sm text-slate-500 shadow-sm">
        Chargement du dossier…
      </div>

      <div v-else-if="loadError" class="rounded-3xl border border-red-200 bg-red-50 p-6 text-sm text-red-700 shadow-sm">
        {{ loadError }}
      </div>

      <template v-else-if="patient">
        <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div class="flex items-start gap-4">
              <div class="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-blue-100 text-2xl font-bold text-blue-700">
                {{ initials }}
              </div>
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Dossier patient</p>
                <h1 class="mt-1 text-2xl font-semibold tracking-tight text-slate-900">
                  {{ patient.prenom }} {{ patient.nom }}
                </h1>
                <div class="mt-2 flex flex-wrap items-center gap-2">
                  <span class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                    {{ patient.numero_dossier }}
                  </span>
                  <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                    {{ ageLabel }}
                  </span>
                  <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                    {{ patient.sexe === 'M' ? 'Masculin' : 'Féminin' }}
                  </span>
                  <span
                    v-if="patient.consentement_donnees"
                    class="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700"
                  >
                    RGPD OK
                  </span>
                </div>
              </div>
            </div>
            <div class="flex flex-wrap gap-2">
              <button
                v-if="auth.canPatientsWrite && !editing"
                type="button"
                class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
                @click="startEdit"
              >
                Modifier
              </button>
              <RouterLink
                v-if="auth.canRdv"
                :to="{ name: 'rendez-vous', query: { patient_id: patient.id } }"
                class="rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700"
              >
                Planifier un RDV
              </RouterLink>
              <RouterLink
                v-if="auth.canHospitalisationAdmit && !hospitalisation"
                :to="{ name: 'hospitalisations', query: { patient_id: patient.id } }"
                class="rounded-2xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700"
              >
                Admission
              </RouterLink>
            </div>
          </div>
        </div>

        <div v-if="message" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          {{ message }}
        </div>
        <div v-if="error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ error }}
        </div>

        <div v-if="editing" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Modifier le dossier</h2>
          <form class="mt-5 grid gap-4 md:grid-cols-2" @submit.prevent="savePatient">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Nom</label>
              <input v-model="editForm.nom" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Prénom</label>
              <input v-model="editForm.prenom" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Date de naissance</label>
              <input v-model="editForm.date_naissance" type="date" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Sexe</label>
              <select v-model="editForm.sexe" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500">
                <option value="M">Masculin</option>
                <option value="F">Féminin</option>
              </select>
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Téléphone</label>
              <input v-model="editForm.telephone" type="tel" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">E-mail</label>
              <input v-model="editForm.email" type="email" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <div class="md:col-span-2">
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Adresse</label>
              <input v-model="editForm.adresse" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <label class="md:col-span-2 flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-3 text-sm text-slate-700">
              <input v-model="editForm.consentement_donnees" class="mt-0.5 h-4 w-4 rounded border-slate-300" type="checkbox" />
              <span>Consentement RGPD enregistré</span>
            </label>
            <div class="md:col-span-2 flex flex-wrap gap-3">
              <button type="submit" class="rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700" :disabled="saving">
                {{ saving ? 'Enregistrement…' : 'Enregistrer' }}
              </button>
              <button type="button" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" @click="cancelEdit">
                Annuler
              </button>
            </div>
          </form>
        </div>

        <div class="flex flex-wrap gap-2 border-b border-slate-200 pb-1">
          <button
            v-for="tab in visibleTabs"
            :key="tab.id"
            type="button"
            class="rounded-t-2xl px-4 py-2.5 text-sm font-semibold transition"
            :class="activeTab === tab.id ? 'bg-white text-blue-700 shadow-sm ring-1 ring-slate-200' : 'text-slate-600 hover:text-slate-900'"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Résumé -->
        <div v-if="activeTab === 'resume'" class="grid gap-4 lg:grid-cols-2">
          <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">Coordonnées</h2>
            <dl class="mt-4 space-y-3 text-sm">
              <div class="flex justify-between gap-4 border-b border-slate-100 pb-3">
                <dt class="text-slate-500">Téléphone</dt>
                <dd class="font-medium text-slate-900">{{ patient.telephone || '—' }}</dd>
              </div>
              <div class="flex justify-between gap-4 border-b border-slate-100 pb-3">
                <dt class="text-slate-500">E-mail</dt>
                <dd class="font-medium text-slate-900">{{ patient.email || '—' }}</dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-slate-500">Adresse</dt>
                <dd class="max-w-xs text-right font-medium text-slate-900">{{ patient.adresse || '—' }}</dd>
              </div>
            </dl>
          </section>

          <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">Accès rapide</h2>
            <div class="mt-4 flex flex-col gap-2">
              <RouterLink
                v-if="auth.canRdvRead"
                :to="{ name: 'rendez-vous', query: { patient_id: patient.id } }"
                class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              >
                Rendez-vous ({{ rendezVous.length }})
              </RouterLink>
              <RouterLink
                v-if="auth.canHospitalisation"
                :to="{ name: 'hospitalisations', query: { patient_id: patient.id } }"
                class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              >
                Hospitalisations
              </RouterLink>
              <RouterLink
                v-if="auth.canPrescriptionsRead && hospitalisation"
                :to="{ name: 'prescriptions', query: { hospitalisation_id: hospitalisation.id } }"
                class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              >
                Prescriptions ({{ prescriptions.length }})
              </RouterLink>
              <RouterLink
                v-if="auth.canFacturationRead"
                :to="{ name: 'facturation', query: { patient_id: patient.id } }"
                class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              >
                Factures ({{ factures.length }})
              </RouterLink>
              <RouterLink
                v-if="canDocuments"
                :to="{ name: 'documents', query: { search: patient.numero_dossier } }"
                class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              >
                Documents ({{ documents.length }})
              </RouterLink>
            </div>
          </section>
        </div>

        <!-- Hospitalisation -->
        <section v-else-if="activeTab === 'hospitalisation'" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 class="text-lg font-semibold text-slate-900">Hospitalisation active</h2>
            <RouterLink
              v-if="auth.canHospitalisation"
              :to="{ name: 'hospitalisations' }"
              class="text-sm font-semibold text-blue-600 hover:text-blue-700"
            >
              Module hospitalisations →
            </RouterLink>
          </div>
          <div v-if="!auth.canHospitalisation" class="mt-4 text-sm text-slate-500">Accès hospitalisations non autorisé pour votre rôle.</div>
          <div v-else-if="!hospitalisation" class="mt-4 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-600">
            Aucune hospitalisation en cours pour ce patient.
            <RouterLink
              v-if="auth.canHospitalisationAdmit"
              :to="{ name: 'hospitalisations', query: { patient_id: patient.id } }"
              class="ml-1 font-semibold text-emerald-700 hover:text-emerald-800"
            >
              Créer une admission
            </RouterLink>
          </div>
          <dl v-else class="mt-4 grid gap-4 sm:grid-cols-2 text-sm">
            <div>
              <dt class="text-slate-500">Motif</dt>
              <dd class="mt-1 font-medium text-slate-900">{{ hospitalisation.motif_admission }}</dd>
            </div>
            <div>
              <dt class="text-slate-500">Admission</dt>
              <dd class="mt-1 font-medium text-slate-900">{{ formatDateTime(hospitalisation.date_admission) }}</dd>
            </div>
            <div>
              <dt class="text-slate-500">Lit</dt>
              <dd class="mt-1 font-medium text-slate-900">
                {{ hospitalisation.batiment_code }}/{{ hospitalisation.service_code }} —
                Ch.{{ hospitalisation.chambre_numero }} Lit {{ hospitalisation.lit_numero }}
              </dd>
            </div>
            <div v-if="auth.canSoinsRead">
              <dt class="text-slate-500">Soins</dt>
              <dd class="mt-1">
                <RouterLink :to="{ name: 'soins' }" class="font-semibold text-blue-600 hover:text-blue-700">
                  Suivi infirmier →
                </RouterLink>
              </dd>
            </div>
          </dl>
        </section>

        <!-- Rendez-vous -->
        <section v-else-if="activeTab === 'rendez-vous'" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 class="text-lg font-semibold text-slate-900">Rendez-vous</h2>
            <RouterLink
              v-if="auth.canRdv"
              :to="{ name: 'rendez-vous', query: { patient_id: patient.id } }"
              class="text-sm font-semibold text-blue-600 hover:text-blue-700"
            >
              Planifier →
            </RouterLink>
          </div>
          <div v-if="rendezVous.length === 0" class="mt-4 text-sm text-slate-500">Aucun rendez-vous enregistré.</div>
          <ul v-else class="mt-4 divide-y divide-slate-100">
            <li v-for="rdv in rendezVous" :key="rdv.id" class="flex flex-col gap-2 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p class="font-semibold text-slate-900">{{ formatDateTime(rdv.date_heure) }}</p>
                <p class="text-sm text-slate-600">{{ rdv.medecin_nom }} · {{ rdv.motif }}</p>
              </div>
              <span class="w-fit rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.15em] text-slate-600">
                {{ statutRdvLabel(rdv.statut) }}
              </span>
            </li>
          </ul>
        </section>

        <!-- Prescriptions -->
        <section v-else-if="activeTab === 'prescriptions'" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 class="text-lg font-semibold text-slate-900">Prescriptions</h2>
            <RouterLink
              v-if="auth.canPrescrire && hospitalisation"
              :to="{ name: 'prescriptions', query: { hospitalisation_id: hospitalisation.id } }"
              class="text-sm font-semibold text-blue-600 hover:text-blue-700"
            >
              Nouvelle prescription →
            </RouterLink>
          </div>
          <div v-if="!hospitalisation" class="mt-4 text-sm text-slate-500">
            Aucune hospitalisation active — les prescriptions sont liées à une admission.
          </div>
          <div v-else-if="prescriptions.length === 0" class="mt-4 text-sm text-slate-500">Aucune prescription pour cette hospitalisation.</div>
          <ul v-else class="mt-4 divide-y divide-slate-100">
            <li v-for="rx in prescriptions" :key="rx.id" class="py-4">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="font-semibold text-slate-900">{{ rx.medecin_nom }}</p>
                <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.15em] text-slate-600">
                  {{ rx.statut }}
                </span>
              </div>
              <p class="mt-1 text-sm text-slate-600">{{ rx.lignes?.length || 0 }} ligne(s) · {{ formatDateTime(rx.created_at) }}</p>
            </li>
          </ul>
        </section>

        <!-- Factures -->
        <section v-else-if="activeTab === 'factures'" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 class="text-lg font-semibold text-slate-900">Factures</h2>
            <RouterLink
              v-if="auth.canFacturationRead"
              :to="{ name: 'facturation', query: { patient_id: patient.id } }"
              class="text-sm font-semibold text-blue-600 hover:text-blue-700"
            >
              Module facturation →
            </RouterLink>
          </div>
          <div v-if="factures.length === 0" class="mt-4 text-sm text-slate-500">Aucune facture pour ce patient.</div>
          <div v-else class="mt-4 overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200 text-sm">
              <thead>
                <tr class="text-left text-slate-600">
                  <th class="px-3 py-3 font-medium">N° facture</th>
                  <th class="px-3 py-3 font-medium">Statut</th>
                  <th class="px-3 py-3 font-medium">Montant</th>
                  <th class="px-3 py-3 font-medium">Reste</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="f in factures" :key="f.id">
                  <td class="px-3 py-3 font-medium text-slate-900">{{ f.numero_facture || '—' }}</td>
                  <td class="px-3 py-3 text-slate-700">{{ f.statut }}</td>
                  <td class="px-3 py-3 text-slate-700">{{ formatMoney(f.montant_total) }}</td>
                  <td class="px-3 py-3 text-slate-700">{{ formatMoney(f.montant_restant) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- Documents -->
        <section v-else-if="activeTab === 'documents'" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 class="text-lg font-semibold text-slate-900">Documents signés</h2>
            <RouterLink
              :to="{ name: 'documents', query: { search: patient.numero_dossier } }"
              class="text-sm font-semibold text-blue-600 hover:text-blue-700"
            >
              Tous les documents →
            </RouterLink>
          </div>
          <div v-if="documents.length === 0" class="mt-4 text-sm text-slate-500">Aucun document trouvé pour ce dossier.</div>
          <ul v-else class="mt-4 divide-y divide-slate-100">
            <li v-for="doc in documents" :key="doc.id" class="flex flex-col gap-2 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p class="font-semibold text-slate-900">{{ doc.type_label }}</p>
                <p class="text-sm text-slate-600">{{ doc.reference }} · {{ formatDateTime(doc.signe_le) }}</p>
              </div>
            </li>
          </ul>
        </section>

        <!-- Assurance -->
        <section v-else-if="activeTab === 'assurance'" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Couverture assurance</h2>
          <div v-if="affiliations.length === 0" class="mt-4 text-sm text-slate-500">Aucune affiliation enregistrée.</div>
          <ul v-else class="mt-4 divide-y divide-slate-100">
            <li v-for="aff in affiliations" :key="aff.id" class="py-4">
              <p class="font-semibold text-slate-900">{{ aff.organisme_nom }}</p>
              <p class="text-sm text-slate-600">
                N° {{ aff.numero_adherent || '—' }} ·
                {{ aff.actif ? 'Active' : 'Inactive' }}
              </p>
            </li>
          </ul>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api, { getErrorMessage, unwrapList } from '../api/client.js'
import { ASSURANCE, DOCUMENTS, hasRole } from '../permissions.js'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const route = useRoute()

const patient = ref(null)
const hospitalisation = ref(null)
const rendezVous = ref([])
const prescriptions = ref([])
const factures = ref([])
const documents = ref([])
const affiliations = ref([])

const loading = ref(true)
const loadError = ref('')
const error = ref('')
const message = ref('')
const saving = ref(false)
const editing = ref(false)
const activeTab = ref('resume')

const editForm = reactive({
  nom: '',
  prenom: '',
  date_naissance: '',
  sexe: 'M',
  telephone: '',
  email: '',
  adresse: '',
  consentement_donnees: false,
  version: 1,
})

const canDocuments = computed(() => hasRole(auth.role, DOCUMENTS))
const canAssurance = computed(() => hasRole(auth.role, ASSURANCE))

const initials = computed(() => {
  if (!patient.value) return '?'
  const p = patient.value.prenom?.[0] || ''
  const n = patient.value.nom?.[0] || ''
  return (p + n).toUpperCase() || '?'
})

const ageLabel = computed(() => {
  if (!patient.value?.date_naissance) return '—'
  const birth = new Date(patient.value.date_naissance)
  const today = new Date()
  let age = today.getFullYear() - birth.getFullYear()
  const m = today.getMonth() - birth.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age -= 1
  return `${age} ans`
})

const visibleTabs = computed(() => {
  const tabs = [{ id: 'resume', label: 'Résumé' }]
  if (auth.canHospitalisation) tabs.push({ id: 'hospitalisation', label: 'Hospitalisation' })
  if (auth.canRdvRead) tabs.push({ id: 'rendez-vous', label: 'Rendez-vous' })
  if (auth.canPrescriptionsRead) tabs.push({ id: 'prescriptions', label: 'Prescriptions' })
  if (auth.canFacturationRead) tabs.push({ id: 'factures', label: 'Factures' })
  if (canDocuments.value) tabs.push({ id: 'documents', label: 'Documents' })
  if (canAssurance.value) tabs.push({ id: 'assurance', label: 'Assurance' })
  return tabs
})

function formatDateTime(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('fr-FR')
  } catch {
    return iso
  }
}

function formatMoney(value) {
  const n = Number(value)
  if (Number.isNaN(n)) return '—'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XAF', maximumFractionDigits: 0 }).format(n)
}

function statutRdvLabel(statut) {
  const labels = {
    planifie: 'Planifié',
    confirme: 'Confirmé',
    annule: 'Annulé',
    termine: 'Terminé',
    absent: 'Absent',
  }
  return labels[statut] || statut
}

function fillEditForm() {
  if (!patient.value) return
  Object.assign(editForm, {
    nom: patient.value.nom,
    prenom: patient.value.prenom,
    date_naissance: patient.value.date_naissance,
    sexe: patient.value.sexe,
    telephone: patient.value.telephone || '',
    email: patient.value.email || '',
    adresse: patient.value.adresse || '',
    consentement_donnees: patient.value.consentement_donnees,
    version: patient.value.version,
  })
}

function startEdit() {
  fillEditForm()
  editing.value = true
}

function cancelEdit() {
  editing.value = false
  error.value = ''
}

async function savePatient() {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    const { data } = await api.patch(`/patients/${patient.value.id}/`, {
      nom: editForm.nom,
      prenom: editForm.prenom,
      date_naissance: editForm.date_naissance,
      sexe: editForm.sexe,
      telephone: editForm.telephone,
      email: editForm.email,
      adresse: editForm.adresse,
      consentement_donnees: editForm.consentement_donnees,
      version: editForm.version,
    })
    patient.value = data
    editing.value = false
    message.value = 'Dossier mis à jour.'
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

async function loadHospitalisation(patientId) {
  try {
    const { data } = await api.get(`/patients/${patientId}/hospitalisation-active/`)
    hospitalisation.value = data
    const { data: rxData } = await api.get(`/hospitalisations/${data.id}/prescriptions/`)
    prescriptions.value = unwrapList(rxData)
  } catch (e) {
    if (e.response?.status === 404) {
      hospitalisation.value = null
      prescriptions.value = []
      return
    }
    throw e
  }
}

async function loadRelated(patientId, numeroDossier) {
  const tasks = []

  if (auth.canRdvRead) {
    tasks.push(
      api.get('/rendez-vous/').then(({ data }) => {
        rendezVous.value = unwrapList(data)
          .filter((r) => r.patient_id === patientId)
          .sort((a, b) => new Date(b.date_heure) - new Date(a.date_heure))
      }),
    )
  }

  if (auth.canFacturationRead) {
    tasks.push(
      api.get('/facturation/factures/').then(({ data }) => {
        factures.value = unwrapList(data).filter((f) => f.patient_id === patientId)
      }),
    )
  }

  if (canDocuments.value) {
    tasks.push(
      api.get(`/documents/?search=${encodeURIComponent(numeroDossier)}`).then(({ data }) => {
        documents.value = unwrapList(data)
      }),
    )
  }

  if (canAssurance.value) {
    tasks.push(
      api.get(`/assurance/affiliations/?patient_id=${patientId}`).then(({ data }) => {
        affiliations.value = unwrapList(data)
      }),
    )
  }

  await Promise.all(tasks)
}

async function loadPatient() {
  loading.value = true
  loadError.value = ''
  error.value = ''
  message.value = ''
  editing.value = false

  const patientId = route.params.id

  try {
    const { data } = await api.get(`/patients/${patientId}/`)
    patient.value = data

    if (auth.canHospitalisation) {
      await loadHospitalisation(patientId)
    }

    await loadRelated(patientId, data.numero_dossier)
  } catch (e) {
    loadError.value = getErrorMessage(e)
    patient.value = null
  } finally {
    loading.value = false
  }
}

watch(
  () => route.params.id,
  (id) => {
    if (id) loadPatient()
  },
)

onMounted(loadPatient)
</script>
