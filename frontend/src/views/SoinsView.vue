<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto max-w-7xl space-y-6">
      <header class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Soins infirmiers</h1>
          <p class="mt-2 text-sm leading-6 text-slate-600">Constantes vitales, plans de soins et suivi des doses</p>
        </div>
      </header>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="grid gap-4">
          <div v-if="message" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
          <div v-if="error" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>

          <div>
            <label class="block text-sm font-medium text-slate-700">Hospitalisation</label>
            <select
              v-model="selectedHospId"
              @change="loadData"
              class="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
            >
              <option value="">— Sélectionner —</option>
              <option v-for="h in hospitalisations" :key="h.id" :value="h.id">
                {{ h.numero_dossier }} — {{ h.patient_prenom }} {{ h.patient_nom }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="selectedHospId" class="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Nouvelle constante vitale</h2>
          <form @submit.prevent="saveConstante" class="mt-6 space-y-4">
            <div class="grid gap-4 md:grid-cols-2">
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-700">Température (°C)</label>
                <input
                  v-model.number="constante.temperature"
                  type="number"
                  step="0.1"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
                />
              </div>
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-700">TA systolique</label>
                <input
                  v-model.number="constante.tension_systolique"
                  type="number"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
                />
              </div>
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-700">TA diastolique</label>
                <input
                  v-model.number="constante.tension_diastolique"
                  type="number"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
                />
              </div>
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-700">FC (bpm)</label>
                <input
                  v-model.number="constante.frequence_cardiaque"
                  type="number"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
                />
              </div>
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-700">SpO₂ (%)</label>
                <input
                  v-model.number="constante.saturation_o2"
                  type="number"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
                />
              </div>
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-700">Glycémie</label>
                <input
                  v-model.number="constante.glycemie"
                  type="number"
                  step="0.1"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
                />
              </div>
            </div>

            <div class="space-y-2">
              <label class="block text-sm font-medium text-slate-700">Notes</label>
              <textarea
                v-model="constante.notes"
                rows="4"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
              />
            </div>

            <button
              type="submit"
              class="inline-flex w-full items-center justify-center rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
            >
              Enregistrer
            </button>
          </form>
        </section>

        <section class="rounded-3xl border border-rose-200 bg-rose-50 p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Doses en retard</h2>
          <div class="mt-4">
            <div v-if="dosesRetard.length === 0" class="rounded-2xl border border-slate-200 bg-white px-4 py-4 text-sm text-slate-600">Aucune dose omise.</div>
            <ul v-else class="space-y-3 text-sm text-slate-700">
              <li v-for="d in dosesRetard" :key="d.id" class="rounded-2xl border border-slate-200 bg-white px-4 py-4">
                {{ d.medicament }} — {{ d.posologie }} <span class="text-slate-500">({{ formatDate(d.heure_prevue) }})</span>
              </li>
            </ul>
          </div>
        </section>
      </div>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Constantes enregistrées</h2>
        <div class="mt-4 space-y-4">
          <div v-if="!selectedHospId" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-600">Sélectionnez une hospitalisation.</div>
          <div v-else-if="constantes.length === 0" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-600">Aucune constante.</div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200 text-sm">
              <thead class="bg-slate-50 text-slate-500">
                <tr>
                  <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Date</th>
                  <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Mesures</th>
                  <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Infirmier</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 bg-white">
                <tr v-for="c in constantes" :key="c.id" class="hover:bg-slate-50">
                  <td class="px-4 py-4 text-slate-700">{{ formatDate(c.mesure_le) }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ formatMesures(c) }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ c.infirmier_nom || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import api, { getErrorMessage, unwrapList } from '../api/client.js'

const hospitalisations = ref([])
const constantes = ref([])
const dosesRetard = ref([])
const selectedHospId = ref('')
const error = ref('')
const message = ref('')

const constante = reactive({
  temperature: null,
  tension_systolique: null,
  tension_diastolique: null,
  frequence_cardiaque: null,
  saturation_o2: null,
  glycemie: null,
  notes: '',
})

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('fr-FR')
  } catch {
    return iso
  }
}

function formatMesures(c) {
  const parts = []
  if (c.temperature != null) parts.push(`T° ${c.temperature}°C`)
  if (c.tension_systolique != null) {
    parts.push(`TA ${c.tension_systolique}/${c.tension_diastolique ?? '—'}`)
  }
  if (c.frequence_cardiaque != null) parts.push(`FC ${c.frequence_cardiaque}`)
  if (c.saturation_o2 != null) parts.push(`SpO₂ ${c.saturation_o2}%`)
  if (c.glycemie != null) parts.push(`Gly ${c.glycemie}`)
  return parts.join(' · ') || '—'
}

async function loadBase() {
  const { data } = await api.get('/hospitalisations/actives/')
  hospitalisations.value = unwrapList(data)
  if (hospitalisations.value.length && !selectedHospId.value) {
    selectedHospId.value = hospitalisations.value[0].id
    await loadData()
  }
  try {
    const dosesRes = await api.get('/soins/alertes/doses-omises/')
    dosesRetard.value = unwrapList(dosesRes.data)
  } catch {
    dosesRetard.value = []
  }
}

async function loadData() {
  if (!selectedHospId.value) return
  error.value = ''
  try {
    const { data } = await api.get(`/hospitalisations/${selectedHospId.value}/constantes-vitales/`)
    constantes.value = unwrapList(data)
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function saveConstante() {
  error.value = ''
  message.value = ''
  const payload = { ...constante }
  Object.keys(payload).forEach((k) => {
    if (payload[k] === null || payload[k] === '') delete payload[k]
  })
  try {
    await api.post(`/hospitalisations/${selectedHospId.value}/constantes-vitales/`, payload)
    message.value = 'Constante enregistrée.'
    Object.assign(constante, {
      temperature: null,
      tension_systolique: null,
      tension_diastolique: null,
      frequence_cardiaque: null,
      saturation_o2: null,
      glycemie: null,
      notes: '',
    })
    await loadData()
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
