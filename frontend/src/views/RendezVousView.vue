<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Rendez-vous</h1>
            <p class="mt-1 text-sm text-slate-600">Planification et suivi des consultations</p>
          </div>
          <button class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" type="button" @click="load">Actualiser</button>
        </div>
      </div>

      <div v-if="message" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
      <div v-if="error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</div>

      <div class="grid gap-4 md:grid-cols-3">
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Aujourd'hui</span>
          <div class="mt-2 text-3xl font-semibold text-slate-900">{{ stats.rdv_aujourdhui }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">À venir (planifiés)</span>
          <div class="mt-2 text-3xl font-semibold text-slate-900">{{ stats.rdv_planifies }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Affichés (filtre)</span>
          <div class="mt-2 text-3xl font-semibold text-slate-900">{{ items.length }}</div>
        </article>
      </div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Calendrier de la semaine</h2>
        <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-7">
          <button
            v-for="day in weekDays"
            :key="day.date"
            type="button"
            class="flex flex-col items-center rounded-3xl border border-slate-200 bg-slate-50 px-3 py-4 text-sm text-slate-700 transition hover:border-blue-400 hover:bg-slate-100"
            :class="day.date === filterDate ? 'border-blue-500 bg-blue-50' : ''"
            @click="selectDay(day.date)"
          >
            <span class="text-xs uppercase tracking-[0.2em] text-slate-500">{{ day.label }}</span>
            <span class="mt-2 text-xl font-semibold text-slate-900">{{ day.num }}</span>
            <span v-if="day.count" class="mt-2 rounded-full bg-blue-600 px-2.5 py-1 text-[11px] font-semibold text-white">{{ day.count }}</span>
          </button>
        </div>
      </div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="grid gap-4 md:grid-cols-2">
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700" for="filter-date">Date</label>
            <input id="filter-date" v-model="filterDate" type="date" @change="onDateChange" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700" for="filter-statut">Statut</label>
            <select id="filter-statut" v-model="filterStatut" @change="loadList" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500">
              <option value="">Tous</option>
              <option value="planifie">Planifié</option>
              <option value="confirme">Validé</option>
              <option value="termine">Terminé</option>
              <option value="annule">Annulé</option>
              <option value="absent">Absent</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="!auth.canRdv && auth.canRdvRead && auth.role === 'comptable'" class="rounded-3xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700">
        Accès en lecture seule (comptable) — planification réservée aux médecins, infirmiers et secrétaires.
      </div>

      <div v-if="auth.canRdv" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Nouveau rendez-vous</h2>
        <form class="mt-5 grid gap-4 md:grid-cols-2" @submit.prevent="createRdv">
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Patient</label>
            <select v-model="form.patient_id" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500">
              <option value="">— Sélectionner —</option>
              <option v-for="p in patients" :key="p.id" :value="p.id">
                {{ p.numero_dossier }} — {{ p.prenom }} {{ p.nom }}
              </option>
            </select>
          </div>
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Médecin</label>
            <select v-model="form.medecin_id" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500">
              <option value="">— Sélectionner —</option>
              <option v-for="m in medecins" :key="m.id" :value="m.id">{{ m.nom }}</option>
            </select>
          </div>
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Date et heure</label>
            <input v-model="form.date_heure" type="datetime-local" required class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Motif</label>
            <input v-model="form.motif" required placeholder="Motif de consultation" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Type de consultation</label>
            <select v-model="form.type_consultation" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500">
              <option value="presentiel">Présentiel</option>
              <option value="teleconsultation">Téléconsultation</option>
            </select>
          </div>
          <div class="md:col-span-2">
            <button class="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700" type="submit" :disabled="saving">Planifier</button>
          </div>
        </form>
      </div>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Planning</h2>
        <div v-if="loading" class="mt-4 text-sm text-slate-500">Chargement…</div>
        <div v-else-if="filteredItems.length === 0" class="mt-4 text-sm text-slate-500">Aucun rendez-vous pour cette période.</div>
        <div v-else class="mt-4 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Heure</th>
                <th class="px-3 py-3 font-medium">Patient</th>
                <th class="px-3 py-3 font-medium">Médecin</th>
                <th class="px-3 py-3 font-medium">Motif</th>
                <th class="px-3 py-3 font-medium">Type</th>
                <th class="px-3 py-3 font-medium">Statut</th>
                <th v-if="auth.canRdv" class="px-3 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="rdv in filteredItems" :key="rdv.id" class="hover:bg-slate-50">
                <td class="px-3 py-3 text-slate-700">{{ formatDateTime(rdv.date_heure) }}</td>
                <td class="px-3 py-3 text-slate-700">{{ rdv.patient_nom }} ({{ rdv.numero_dossier }})</td>
                <td class="px-3 py-3 text-slate-700">{{ rdv.medecin_nom }}</td>
                <td class="px-3 py-3 text-slate-700">{{ rdv.motif }}</td>
                <td class="px-3 py-3 text-slate-700">
                  <span v-if="rdv.type_consultation === 'teleconsultation'" class="rounded-full bg-sky-100 px-2.5 py-1 text-xs font-semibold text-sky-700">Visio</span>
                  <span v-else class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">Présentiel</span>
                  <a v-if="rdv.lien_visio" :href="rdv.lien_visio" target="_blank" rel="noopener noreferrer" class="ml-2 text-xs font-semibold text-blue-600 hover:text-blue-700">Lien</a>
                </td>
                <td class="px-3 py-3"><span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600">{{ statutLabel(rdv.statut) }}</span></td>
                <td v-if="auth.canRdv" class="px-3 py-3">
                  <button
                    v-if="['planifie', 'confirme'].includes(rdv.statut)"
                    type="button"
                    class="rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
                    @click="openStaffPanel(rdv)"
                  >
                    Gérer
                  </button>
                  <span v-else class="text-sm text-slate-500">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <RdvStaffPanel v-model:open="staffPanelOpen" :rdv="selectedRdv" :medecins="medecins" @success="onStaffSuccess" />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import api, { getErrorMessage, unwrapList } from '../api/client.js'
import RdvStaffPanel from '../components/RdvStaffPanel.vue'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const route = useRoute()
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const message = ref('')
const items = ref([])
const patients = ref([])
const medecins = ref([])
const stats = reactive({ rdv_aujourdhui: 0, rdv_planifies: 0 })

const filterDate = ref(new Date().toISOString().slice(0, 10))
const filterStatut = ref('')
const weekDays = ref([])
const staffPanelOpen = ref(false)
const selectedRdv = ref(null)
const patientFilter = ref('')

const filteredItems = computed(() => {
  if (!patientFilter.value) return items.value
  return items.value.filter((rdv) => rdv.patient_id === patientFilter.value)
})

const form = reactive({
  patient_id: '',
  medecin_id: '',
  date_heure: '',
  motif: '',
  type_consultation: 'presentiel',
})

const statutLabels = {
  planifie: 'Planifié',
  confirme: 'Validé',
  annule: 'Annulé',
  termine: 'Terminé',
  absent: 'Absent',
}

function statutLabel(s) {
  return statutLabels[s] || s
}

function formatDateTime(iso) {
  try {
    return new Date(iso).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

function toIsoDateTime(localValue) {
  if (!localValue) return null
  return new Date(localValue).toISOString()
}

function dayMeta(iso, count) {
  const d = new Date(iso + 'T12:00:00')
  return {
    date: iso,
    label: d.toLocaleDateString('fr-FR', { weekday: 'short' }),
    num: d.getDate(),
    count,
  }
}

async function loadWeek() {
  try {
    const { data } = await api.get(`/rendez-vous/semaine/?date=${filterDate.value}`)
    const rows = Array.isArray(data) ? data : []
    weekDays.value = rows.map((row) => dayMeta(row.date, row.count))
  } catch {
    weekDays.value = []
  }
}

async function onDateChange() {
  await loadWeek()
  await loadList()
}

async function selectDay(iso) {
  filterDate.value = iso
  await onDateChange()
}

async function loadList() {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (filterDate.value) params.set('date', filterDate.value)
    if (filterStatut.value) params.set('statut', filterStatut.value)
    const qs = params.toString()
    const { data } = await api.get(`/rendez-vous/${qs ? `?${qs}` : ''}`)
    items.value = unwrapList(data)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function load() {
  try {
    const [statsRes, patientsRes, medecinsRes] = await Promise.all([
      api.get('/rendez-vous/stats/'),
      auth.canRdv ? api.get('/patients/') : Promise.resolve({ data: { items: [] } }),
      auth.canRdv ? api.get('/rendez-vous/medecins/') : Promise.resolve({ data: { items: [] } }),
    ])
    stats.rdv_aujourdhui = statsRes.data.rdv_aujourdhui
    stats.rdv_planifies = statsRes.data.rdv_planifies
    patients.value = unwrapList(patientsRes.data)
    medecins.value = unwrapList(medecinsRes.data)
    await loadWeek()
    await loadList()
    const pid = route.query.patient_id
    if (pid) {
      patientFilter.value = String(pid)
      if (auth.canRdv) form.patient_id = String(pid)
    }
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function createRdv() {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    await api.post('/rendez-vous/', {
      patient_id: form.patient_id,
      medecin_id: Number(form.medecin_id),
      date_heure: toIsoDateTime(form.date_heure),
      motif: form.motif,
      type_consultation: form.type_consultation,
    })
    message.value = form.type_consultation === 'teleconsultation'
      ? 'Rendez-vous téléconsultation planifié (lien visio généré).'
      : 'Rendez-vous planifié.'
    form.motif = ''
    form.date_heure = ''
    await load()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

function openStaffPanel(rdv) {
  selectedRdv.value = rdv
  staffPanelOpen.value = true
}

async function onStaffSuccess(msg) {
  message.value = msg
  error.value = ''
  await load()
}

onMounted(load)
</script>


