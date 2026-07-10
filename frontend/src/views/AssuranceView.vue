<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto max-w-6xl space-y-6">
      <div class="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Assurance & Mutuelles</h1>
          <p class="mt-1 text-sm text-slate-600">Gestion des tiers payants et conventions d'assurance</p>
        </div>
        <div class="flex gap-2">
          <button class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" type="button" @click="loadAll">Actualiser</button>
          <button class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800" type="button" @click="openNewConvention">+ Nouvelle convention</button>
        </div>
      </div>

      <div v-if="message" class="rounded-3xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700 shadow-sm">{{ message }}</div>
      <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 shadow-sm">{{ error }}</div>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="grid gap-4 sm:grid-cols-3">
          <article class="rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <span class="block text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Conventions actives</span>
            <strong class="mt-3 block text-2xl text-slate-900">{{ stats.conventions_actives }}</strong>
          </article>
          <article class="rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <span class="block text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Tiers payants</span>
            <strong class="mt-3 block text-2xl text-slate-900">{{ stats.tiers_payants }}</strong>
          </article>
          <article class="rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <span class="block text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Taux remboursement moyen</span>
            <strong class="mt-3 block text-2xl text-slate-900">{{ stats.taux_remboursement_moyen }}%</strong>
          </article>
        </div>
      </section>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-6 flex flex-wrap gap-2 rounded-3xl bg-slate-50 p-2">
          <button
            v-for="tab in mainTabs"
            :key="tab.id"
            type="button"
            class="rounded-2xl px-4 py-2 text-sm font-semibold transition"
            :class="activeMainTab === tab.id ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-100'"
            @click="activeMainTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <template v-if="activeMainTab === 'conventions'">
        <div class="grid gap-4 sm:grid-cols-[1fr_220px]">
          <input
            v-model="search"
            type="search"
            placeholder="Rechercher une convention ou assurance…"
            class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
            @input="debouncedLoad"
          />
          <select
            v-model="statusFilter"
            class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
            @change="loadOrganismes"
          >
            <option value="">Tous les statuts</option>
            <option value="active">Actif</option>
            <option value="inactive">Inactif</option>
          </select>
        </div>

        <div v-if="loading" class="mt-6 rounded-3xl border border-slate-200 bg-slate-50 px-4 py-5 text-sm text-slate-600">Chargement…</div>
        <div v-else-if="tierPayants.length === 0" class="mt-6 rounded-3xl border border-slate-200 bg-slate-50 px-4 py-5 text-sm text-slate-600">Aucune convention trouvée.</div>

        <div v-else class="mt-6 overflow-hidden rounded-3xl border border-slate-200">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-slate-600">
              <tr>
                <th class="px-4 py-3 text-left font-medium">Code</th>
                <th class="px-4 py-3 text-left font-medium">Assurance</th>
                <th class="px-4 py-3 text-left font-medium">Taux de couverture</th>
                <th class="px-4 py-3 text-left font-medium">Affiliations</th>
                <th class="px-4 py-3 text-left font-medium">Statut</th>
                <th class="px-4 py-3 text-left font-medium">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 bg-white">
              <tr v-for="convention in tierPayants" :key="convention.id" class="hover:bg-slate-50">
                <td class="px-4 py-4 font-mono text-xs text-slate-500">{{ convention.code }}</td>
                <td class="px-4 py-4 font-medium text-slate-700">{{ convention.assurance }}</td>
                <td class="px-4 py-4 text-slate-700">{{ convention.coverage }}%</td>
                <td class="px-4 py-4 text-slate-700">
                  <span class="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">{{ convention.conventions }}</span>
                </td>
                <td class="px-4 py-4">
                  <span :class="['inline-flex rounded-full px-3 py-1 text-xs font-semibold', convention.active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600']">
                    {{ convention.active ? 'Actif' : 'Inactif' }}
                  </span>
                </td>
                <td class="px-4 py-4">
                  <div class="flex flex-wrap gap-2">
                    <button class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50" @click="editConvention(convention)">Éditer</button>
                    <button class="inline-flex items-center justify-center rounded-2xl bg-rose-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-rose-700" @click="requestDeleteConvention(convention)">Supprimer</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        </template>

        <template v-else>
          <div class="mb-4 flex justify-end">
            <button class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800" type="button" @click="openNewAffiliation">+ Nouvelle affiliation</button>
          </div>
          <div v-if="affiliationsLoading" class="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-5 text-sm text-slate-600">Chargement…</div>
          <div v-else-if="affiliations.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-5 text-sm text-slate-600">Aucune affiliation enregistrée.</div>
          <div v-else class="overflow-hidden rounded-3xl border border-slate-200">
            <table class="min-w-full divide-y divide-slate-200 text-sm">
              <thead class="bg-slate-50 text-slate-600">
                <tr>
                  <th class="px-4 py-3 text-left font-medium">Patient</th>
                  <th class="px-4 py-3 text-left font-medium">Organisme</th>
                  <th class="px-4 py-3 text-left font-medium">N° adhérent</th>
                  <th class="px-4 py-3 text-left font-medium">Période</th>
                  <th class="px-4 py-3 text-left font-medium">Statut</th>
                  <th class="px-4 py-3 text-left font-medium">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 bg-white">
                <tr v-for="aff in affiliations" :key="aff.id" class="hover:bg-slate-50">
                  <td class="px-4 py-4 font-medium text-slate-700">{{ aff.patient_nom }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ aff.organisme_nom }}</td>
                  <td class="px-4 py-4 font-mono text-xs text-slate-500">{{ aff.numero_adherent || '—' }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ aff.date_debut }} → {{ aff.date_fin || '—' }}</td>
                  <td class="px-4 py-4">
                    <span :class="aff.actif ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'" class="inline-flex rounded-full px-3 py-1 text-xs font-semibold">
                      {{ aff.actif ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-4 py-4">
                    <div class="flex flex-wrap gap-2">
                      <button class="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" @click="editAffiliation(aff)">Éditer</button>
                      <button class="rounded-2xl bg-rose-600 px-3 py-2 text-sm font-semibold text-white hover:bg-rose-700" @click="requestDeleteAffiliation(aff)">Supprimer</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </section>

      <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4" @click.self="closeForm">
        <form class="w-full max-w-lg space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-xl" @submit.prevent="saveConvention">
          <h2 class="text-lg font-semibold text-slate-900">{{ editingId ? 'Modifier la convention' : 'Nouvelle convention' }}</h2>
          <input v-model="form.code" :disabled="!!editingId" required placeholder="Code (ex. CNSS)" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400 disabled:opacity-60" />
          <input v-model="form.nom" required placeholder="Nom de l'organisme" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" />
          <input v-model.number="form.taux_couverture" required type="number" min="0" max="100" placeholder="Taux de couverture (%)" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" />
          <input v-model="form.contact_email" type="email" placeholder="Email contact" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" />
          <input v-model="form.contact_telephone" placeholder="Téléphone contact" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" />
          <label class="flex items-center gap-2 text-sm text-slate-700">
            <input v-model="form.actif" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
            Convention active
          </label>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" class="rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50" @click="closeForm">Annuler</button>
            <button type="submit" class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800" :disabled="saving">{{ saving ? 'Enregistrement…' : 'Enregistrer' }}</button>
          </div>
        </form>
      </div>

      <div v-if="showAffForm" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4" @click.self="closeAffForm">
        <form class="w-full max-w-lg space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-xl" @submit.prevent="saveAffiliation">
          <h2 class="text-lg font-semibold text-slate-900">{{ editingAffId ? 'Modifier l\'affiliation' : 'Nouvelle affiliation' }}</h2>
          <select v-model="affForm.patient_id" required :disabled="!!editingAffId" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400 disabled:opacity-60">
            <option value="">— Patient —</option>
            <option v-for="p in patients" :key="p.id" :value="p.id">{{ p.numero_dossier }} — {{ p.prenom }} {{ p.nom }}</option>
          </select>
          <select v-model="affForm.organisme_id" required :disabled="!!editingAffId" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400 disabled:opacity-60">
            <option value="">— Organisme —</option>
            <option v-for="org in tierPayants" :key="org.id" :value="org.id">{{ org.assurance }} ({{ org.code }})</option>
          </select>
          <input v-model="affForm.numero_adherent" placeholder="N° adhérent" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" />
          <input v-model="affForm.date_debut" required type="date" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" />
          <input v-model="affForm.date_fin" type="date" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" />
          <label class="flex items-center gap-2 text-sm text-slate-700">
            <input v-model="affForm.actif" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
            Affiliation active
          </label>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" class="rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50" @click="closeAffForm">Annuler</button>
            <button type="submit" class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800" :disabled="saving">{{ saving ? 'Enregistrement…' : 'Enregistrer' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <ConfirmDialog
    :open="confirmDelete.open"
    title="Confirmer la suppression"
    :message="confirmDelete.message"
    confirm-label="Supprimer"
    :danger="true"
    :loading="deleting"
    @confirm="confirmDeletion"
    @cancel="confirmDelete.open = false"
  />
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import api, { getErrorMessage, unwrapList } from '../api/client.js'
import { showToast } from '../composables/useToast.js'

const mainTabs = [
  { id: 'conventions', label: 'Conventions' },
  { id: 'affiliations', label: 'Affiliations patients' },
]
const activeMainTab = ref('conventions')

const tierPayants = ref([])
const affiliations = ref([])
const patients = ref([])
const stats = ref({ conventions_actives: 0, tiers_payants: 0, taux_remboursement_moyen: 0 })
const loading = ref(true)
const affiliationsLoading = ref(false)
const saving = ref(false)
const error = ref('')
const message = ref('')
const confirmDelete = ref({ open: false, message: '', type: null, item: null })
const deleting = ref(false)
const search = ref('')
const statusFilter = ref('')
const showForm = ref(false)
const showAffForm = ref(false)
const editingId = ref(null)
const editingAffId = ref(null)
const form = ref(emptyForm())
const affForm = ref(emptyAffForm())

let debounceTimer = null

function emptyForm() {
  return { code: '', nom: '', taux_couverture: 80, actif: true, contact_email: '', contact_telephone: '' }
}

function emptyAffForm() {
  return { patient_id: '', organisme_id: '', numero_adherent: '', date_debut: new Date().toISOString().slice(0, 10), date_fin: '', actif: true }
}

function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadOrganismes, 300)
}

async function loadStats() {
  const { data } = await api.get('/assurance/stats/')
  stats.value = data
}

async function loadOrganismes() {
  const params = new URLSearchParams()
  if (search.value.trim()) params.set('search', search.value.trim())
  if (statusFilter.value === 'active') params.set('actif', 'true')
  if (statusFilter.value === 'inactive') params.set('actif', 'false')
  const qs = params.toString()
  const { data } = await api.get(`/assurance/organismes/${qs ? `?${qs}` : ''}`)
  tierPayants.value = unwrapList(data)
}

async function loadAffiliations() {
  affiliationsLoading.value = true
  try {
    const { data } = await api.get('/assurance/affiliations/')
    affiliations.value = unwrapList(data)
  } finally {
    affiliationsLoading.value = false
  }
}

async function loadPatients() {
  const { data } = await api.get('/patients/')
  patients.value = unwrapList(data)
}

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([loadStats(), loadOrganismes(), loadAffiliations(), loadPatients()])
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

function openNewConvention() {
  editingId.value = null
  form.value = emptyForm()
  showForm.value = true
}

function editConvention(convention) {
  editingId.value = convention.id
  form.value = {
    code: convention.code,
    nom: convention.assurance,
    taux_couverture: convention.coverage,
    actif: convention.active,
    contact_email: convention.contact_email || '',
    contact_telephone: convention.contact_telephone || '',
  }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingId.value = null
}

async function saveConvention() {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    if (editingId.value) {
      await api.patch(`/assurance/organismes/${editingId.value}/`, {
        nom: form.value.nom,
        taux_couverture: form.value.taux_couverture,
        actif: form.value.actif,
        contact_email: form.value.contact_email,
        contact_telephone: form.value.contact_telephone,
      })
      message.value = 'Convention mise à jour.'
    } else {
      await api.post('/assurance/organismes/', form.value)
      message.value = 'Convention créée.'
    }
    closeForm()
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

function requestDeleteConvention(convention) {
  confirmDelete.value = {
    open: true,
    message: `Supprimer la convention ${convention.assurance} ? Cette action est irréversible.`,
    type: 'convention',
    item: convention,
  }
}

function requestDeleteAffiliation(aff) {
  confirmDelete.value = {
    open: true,
    message: `Supprimer l'affiliation de ${aff.patient_nom} ? Cette action est irréversible.`,
    type: 'affiliation',
    item: aff,
  }
}

async function confirmDeletion() {
  const { type, item } = confirmDelete.value
  if (!item) return
  error.value = ''
  deleting.value = true
  try {
    if (type === 'convention') {
      await api.delete(`/assurance/organismes/${item.id}/`)
      message.value = 'Convention supprimée.'
      showToast('Convention supprimée.', 'success')
      await loadAll()
    } else if (type === 'affiliation') {
      await api.delete(`/assurance/affiliations/${item.id}/`)
      message.value = 'Affiliation supprimée.'
      showToast('Affiliation supprimée.', 'success')
      await loadAffiliations()
      await loadStats()
    }
    confirmDelete.value.open = false
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    deleting.value = false
  }
}

function openNewAffiliation() {
  editingAffId.value = null
  affForm.value = emptyAffForm()
  showAffForm.value = true
}

function editAffiliation(aff) {
  editingAffId.value = aff.id
  affForm.value = {
    patient_id: aff.patient_id,
    organisme_id: aff.organisme_id,
    numero_adherent: aff.numero_adherent || '',
    date_debut: aff.date_debut,
    date_fin: aff.date_fin || '',
    actif: aff.actif,
  }
  showAffForm.value = true
}

function closeAffForm() {
  showAffForm.value = false
  editingAffId.value = null
}

async function saveAffiliation() {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    const body = {
      numero_adherent: affForm.value.numero_adherent,
      date_debut: affForm.value.date_debut,
      date_fin: affForm.value.date_fin || null,
      actif: affForm.value.actif,
    }
    if (editingAffId.value) {
      await api.patch(`/assurance/affiliations/${editingAffId.value}/`, body)
      message.value = 'Affiliation mise à jour.'
    } else {
      await api.post('/assurance/affiliations/', {
        ...body,
        patient_id: affForm.value.patient_id,
        organisme_id: affForm.value.organisme_id,
      })
      message.value = 'Affiliation créée.'
    }
    closeAffForm()
    await loadAffiliations()
    await loadStats()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

watch(activeMainTab, (tab) => {
  if (tab === 'affiliations') loadAffiliations()
})

onMounted(loadAll)
</script>
