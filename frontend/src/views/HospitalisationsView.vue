<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <div class="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Hospitalisations</h1>
          <p class="mt-1 text-sm text-slate-600">Admissions, lits et sorties patients</p>
        </div>
        <button
          v-if="auth.canHospitalisationAdmit"
          class="inline-flex items-center justify-center rounded-2xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700"
          type="button"
          @click="showAdmission = !showAdmission"
        >
          {{ showAdmission ? 'Annuler' : 'Nouvelle admission' }}
        </button>
      </div>

      <div v-if="message" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
      <div v-if="error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</div>

      <div v-if="showAdmission" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Admission patient</h2>
        <form class="mt-5 space-y-4" @submit.prevent="admettre">
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-700">Patient</label>
              <select v-model="admission.patient_id" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none ring-0 focus:border-blue-500">
                <option value="">— Sélectionner —</option>
                <option v-for="p in patients" :key="p.id" :value="p.id">
                  {{ p.numero_dossier }} — {{ p.prenom }} {{ p.nom }}
                </option>
              </select>
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-700">Lit disponible</label>
              <select v-model="admission.lit_id" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none ring-0 focus:border-blue-500" @change="onLitChange">
                <option value="">— Sélectionner —</option>
                <option v-for="l in lits" :key="l.id" :value="l.id">
                  {{ l.batiment_code }}/{{ l.service_code }} Ch.{{ l.chambre_numero }} Lit {{ l.numero }}
                </option>
              </select>
            </div>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium text-slate-700">Motif d'admission</label>
            <textarea v-model="admission.motif_admission" required class="min-h-28 w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none ring-0 focus:border-blue-500" />
          </div>
          <button class="inline-flex items-center justify-center rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700" type="submit" :disabled="saving">Admettre</button>
        </form>
      </div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Hospitalisations actives</h2>
        <div v-if="loading" class="mt-4 text-sm text-slate-500">Chargement…</div>
        <div v-else-if="hospitalisations.length === 0" class="mt-4 text-sm text-slate-500">Aucune hospitalisation active.</div>
        <div v-else class="mt-4 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Patient</th>
                <th class="px-3 py-3 font-medium">Lit</th>
                <th class="px-3 py-3 font-medium">Motif</th>
                <th class="px-3 py-3 font-medium">Admission</th>
                <th v-if="auth.canHospitalisationSortie" class="px-3 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="h in hospitalisations" :key="h.id" class="hover:bg-slate-50">
                <td class="px-3 py-3">
                  <RouterLink
                    v-if="h.patient_id"
                    :to="{ name: 'patient-detail', params: { id: h.patient_id } }"
                    class="font-medium text-blue-600 hover:text-blue-700"
                  >
                    {{ h.patient_prenom }} {{ h.patient_nom }} ({{ h.numero_dossier }})
                  </RouterLink>
                  <span v-else class="text-slate-700">{{ h.patient_prenom }} {{ h.patient_nom }} ({{ h.numero_dossier }})</span>
                </td>
                <td class="px-3 py-3 text-slate-700">{{ h.batiment_code }}/{{ h.service_code }} Ch.{{ h.chambre_numero }} Lit {{ h.lit_numero }}</td>
                <td class="px-3 py-3 text-slate-700">{{ h.motif_admission }}</td>
                <td class="px-3 py-3 text-slate-700">{{ formatDate(h.date_admission) }}</td>
                <td v-if="auth.canHospitalisationSortie" class="px-3 py-3">
                  <button class="rounded-xl bg-red-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-red-700" @click="requestSortie(h)">Sortie</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <ConfirmDialog
    :open="confirmSortie.open"
    title="Enregistrer la sortie"
    :message="confirmSortie.message"
    confirm-label="Confirmer la sortie"
    danger
    :loading="saving"
    @confirm="confirmSortiePatient"
    @cancel="confirmSortie.open = false"
  />
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import api, { getErrorMessage, unwrapList } from '../api/client.js'
import { showToast } from '../composables/useToast.js'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const route = useRoute()
const hospitalisations = ref([])
const patients = ref([])
const lits = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const message = ref('')
const showAdmission = ref(false)
const confirmSortie = ref({ open: false, message: '', hospitalisation: null })

const admission = reactive({
  patient_id: '',
  lit_id: '',
  lit_version: 1,
  motif_admission: '',
})

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('fr-FR')
  } catch {
    return iso
  }
}

function onLitChange() {
  const lit = lits.value.find((l) => l.id === admission.lit_id)
  admission.lit_version = lit?.version || 1
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const requests = [api.get('/hospitalisations/actives/')]
    if (auth.canHospitalisationAdmit) {
      requests.push(api.get('/patients/'), api.get('/logistique/lits/', { params: { disponible: true } }))
    }
    const results = await Promise.all(requests)
    hospitalisations.value = unwrapList(results[0].data)
    if (auth.canHospitalisationAdmit && results.length > 2) {
      patients.value = unwrapList(results[1].data)
      lits.value = unwrapList(results[2].data)
    }
    const pid = route.query.patient_id
    if (pid && auth.canHospitalisationAdmit) {
      admission.patient_id = String(pid)
      showAdmission.value = true
    }
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function admettre() {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    await api.post('/hospitalisations/admission/', admission)
    message.value = 'Patient admis.'
    showAdmission.value = false
    admission.patient_id = ''
    admission.lit_id = ''
    admission.motif_admission = ''
    await load()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

function requestSortie(h) {
  confirmSortie.value = {
    open: true,
    message: `Confirmer la sortie de ${h.patient_prenom} ${h.patient_nom} ?`,
    hospitalisation: h,
  }
}

async function confirmSortiePatient() {
  const h = confirmSortie.value.hospitalisation
  if (!h) return
  saving.value = true
  error.value = ''
  try {
    await api.post(`/hospitalisations/${h.id}/sortie/`, { version: h.version })
    confirmSortie.value.open = false
    message.value = 'Sortie enregistrée.'
    showToast('Sortie enregistrée.', 'success')
    await load()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

