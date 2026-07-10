<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Prescriptions</h1>
        <p class="mt-1 text-sm text-slate-600">Ordonnances, lignes médicamenteuses et validation</p>
      </div>

      <div v-if="message" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
      <div v-if="error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <label class="mb-2 block text-sm font-medium text-slate-700" for="hospitalisation">Hospitalisation active</label>
        <select id="hospitalisation" v-model="selectedHospId" @change="loadPrescriptions" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500 md:max-w-md">
          <option value="">— Sélectionner —</option>
          <option v-for="h in hospitalisations" :key="h.id" :value="h.id">
            {{ h.numero_dossier }} — {{ h.patient_prenom }} {{ h.patient_nom }}
          </option>
        </select>
      </div>

      <div v-if="selectedHospId && !auth.canPrescrire" class="rounded-2xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700">
        Consultation des ordonnances — création et validation réservées aux médecins.
      </div>

      <div v-if="selectedHospId && auth.canPrescrire" class="grid gap-6 xl:grid-cols-2">
        <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Nouvelle prescription</h2>
          <form class="mt-5 space-y-4" @submit.prevent="createPrescription">
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">Diagnostics CIM-10</label>
              <select v-model="form.codes_cim10" multiple size="4" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500">
                <option v-for="d in diagnostics" :key="d.code" :value="d.code">
                  {{ d.code }} — {{ d.libelle }}
                </option>
              </select>
            </div>
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">Observations</label>
              <textarea v-model="form.observations" class="min-h-24 w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <button class="rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700" type="submit" :disabled="saving">Créer brouillon</button>
          </form>
        </div>

        <div v-if="activePrescription" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Brouillon en cours</h2>
          <div class="mt-3 flex flex-wrap items-center gap-2">
            <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600">{{ activePrescription.statut }}</span>
            <span class="text-sm text-slate-500">v{{ activePrescription.version }}</span>
          </div>
          <div class="mt-5 space-y-4">
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">Médicament</label>
              <input v-model="ligne.medicament" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">Posologie</label>
              <input v-model="ligne.posologie" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">Durée</label>
              <input v-model="ligne.duree_traitement" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <div class="flex flex-wrap gap-3">
              <button class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" @click="addLigne">Ajouter ligne</button>
              <button class="rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700" @click="valider">Valider prescription</button>
            </div>
            <ul v-if="activePrescription.lignes?.length" class="space-y-2 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
              <li v-for="l in activePrescription.lignes" :key="l.id" class="flex items-center justify-between gap-3">
                <span>{{ l.medicament }} — {{ l.posologie }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Historique</h2>
        <div v-if="!selectedHospId" class="mt-4 text-sm text-slate-500">Sélectionnez une hospitalisation.</div>
        <div v-else-if="prescriptions.length === 0" class="mt-4 text-sm text-slate-500">Aucune prescription.</div>
        <div v-else class="mt-4 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Statut</th>
                <th class="px-3 py-3 font-medium">Médicaments</th>
                <th class="px-3 py-3 font-medium">Diagnostics</th>
                <th class="px-3 py-3 font-medium">Date</th>
                <th class="px-3 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="p in prescriptions" :key="p.id" class="hover:bg-slate-50">
                <td class="px-3 py-3"><span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600">{{ p.statut }}</span></td>
                <td class="px-3 py-3 text-slate-700">{{ p.lignes?.map((l) => l.medicament).join(', ') || '—' }}</td>
                <td class="px-3 py-3 text-slate-700">{{ p.diagnostics?.map((d) => d.code_cim10).join(', ') || '—' }}</td>
                <td class="px-3 py-3 text-slate-700">{{ formatDate(p.created_at) }}</td>
                <td class="px-3 py-3">
                  <button
                    v-if="p.statut === 'validee'"
                    class="rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
                    @click="telechargerPdf(p)"
                  >
                    PDF
                  </button>
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
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import api, { downloadPdf, getErrorMessage, unwrapList } from '../api/client.js'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const route = useRoute()
const hospitalisations = ref([])
const diagnostics = ref([])
const prescriptions = ref([])
const selectedHospId = ref('')
const saving = ref(false)
const error = ref('')
const message = ref('')

const form = reactive({ observations: '', codes_cim10: [] })
const ligne = reactive({ medicament: '', posologie: '', duree_traitement: '' })

const activePrescription = computed(() =>
  prescriptions.value.find((p) => p.statut === 'brouillon'),
)

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('fr-FR')
  } catch {
    return iso
  }
}

async function loadBase() {
  if (!auth.canHospitalisation) {
    error.value = 'Accès hospitalisations requis pour consulter les prescriptions.'
    return
  }
  const [hospRes, cimRes] = await Promise.all([
    api.get('/hospitalisations/actives/'),
    api.get('/diagnostics-cim10/'),
  ])
  hospitalisations.value = unwrapList(hospRes.data)
  diagnostics.value = unwrapList(cimRes.data)
  const queryHospId = route.query.hospitalisation_id
  if (queryHospId && hospitalisations.value.some((h) => h.id === queryHospId)) {
    selectedHospId.value = String(queryHospId)
    await loadPrescriptions()
  } else if (hospitalisations.value.length && !selectedHospId.value) {
    selectedHospId.value = hospitalisations.value[0].id
    await loadPrescriptions()
  }
}

async function loadPrescriptions() {
  if (!selectedHospId.value) return
  error.value = ''
  try {
    const { data } = await api.get(`/hospitalisations/${selectedHospId.value}/prescriptions/`)
    prescriptions.value = unwrapList(data)
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function createPrescription() {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    await api.post(`/hospitalisations/${selectedHospId.value}/prescriptions/`, {
      observations: form.observations,
      codes_cim10: form.codes_cim10,
    })
    message.value = 'Prescription créée.'
    form.observations = ''
    form.codes_cim10 = []
    await loadPrescriptions()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

async function addLigne() {
  if (!activePrescription.value) return
  error.value = ''
  try {
    await api.post(`/prescriptions/${activePrescription.value.id}/lignes/`, ligne)
    message.value = 'Ligne ajoutée.'
    ligne.medicament = ''
    ligne.posologie = ''
    ligne.duree_traitement = ''
    await loadPrescriptions()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function valider() {
  if (!activePrescription.value) return
  error.value = ''
  try {
    await api.post(`/prescriptions/${activePrescription.value.id}/valider/`, {
      version: activePrescription.value.version,
    })
    message.value = 'Prescription validée et verrouillée.'
    await loadPrescriptions()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function telechargerPdf(prescription) {
  error.value = ''
  try {
    await downloadPdf(`/prescriptions/${prescription.id}/pdf/`, `ordonnance-${prescription.id}.pdf`)
    message.value = 'Ordonnance PDF téléchargée.'
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

onMounted(async () => {
  try {
    await loadBase()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
})
</script>


