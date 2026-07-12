<template>
  <div class="tech-dashboard min-h-screen text-slate-900">
    <a href="#main-staff" class="skip-link">Aller au contenu principal</a>
    <header class="border-b border-slate-200 bg-white/80 backdrop-blur">
      <div class="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-6 sm:px-6 lg:flex-row lg:items-end lg:justify-between lg:px-8">
        <div class="flex items-center gap-4">
          <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600 text-xl font-semibold text-white shadow-lg">
            ⊕
          </div>
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Centre Hospitalier SGHL</h1>
            <p class="text-sm text-slate-600">🧬 Tech-Health · Système de gestion médicale</p>
          </div>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
          <p class="text-sm uppercase tracking-[0.2em] text-slate-500">{{ todayLabel }}</p>
          <h2 class="text-lg font-semibold text-slate-900">Bienvenue, {{ auth.fullName || 'équipe' }}</h2>
        </div>
      </div>
    </header>

      <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 shadow-sm">
        {{ error }}
      </div>

      <section id="main-staff" aria-label="Indicateurs clés">
      <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-center gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-50 text-xl">👤</div>
            <span class="text-sm font-semibold text-slate-700">Patients actifs</span>
          </div>
          <div class="text-3xl font-semibold text-slate-900">{{ stats.patientsActifs }}</div>
          <p class="mt-1 text-sm text-slate-600">Hospitalisés actuellement</p>
          <RouterLink v-if="auth.canHospitalisation" to="/hospitalisations" class="mt-4 inline-flex text-sm font-semibold text-blue-600 hover:text-blue-700">
            Voir les séjours →
          </RouterLink>
        </article>

        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-center gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-50 text-xl">📅</div>
            <span class="text-sm font-semibold text-slate-700">Rendez-vous du jour</span>
          </div>
          <div class="text-3xl font-semibold text-slate-900">{{ stats.rdvToday }}</div>
          <p class="mt-1 text-sm text-slate-600">Planifiés ou confirmés</p>
          <RouterLink v-if="auth.canRdvRead" to="/rendez-vous" class="mt-4 inline-flex text-sm font-semibold text-blue-600 hover:text-blue-700">
            Ouvrir le planning →
          </RouterLink>
        </article>

        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-center gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-50 text-xl">💊</div>
            <span class="text-sm font-semibold text-slate-700">Prescriptions délivrées</span>
          </div>
          <div class="text-3xl font-semibold text-slate-900">{{ stats.prescriptionsPending }}</div>
          <p class="mt-1 text-sm text-slate-600">En attente de validation</p>
          <RouterLink v-if="auth.canPrescrire" to="/prescriptions" class="mt-4 inline-flex text-sm font-semibold text-blue-600 hover:text-blue-700">
            Valider les ordonnances →
          </RouterLink>
        </article>

        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-center gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-amber-50 text-xl">🛏️</div>
            <span class="text-sm font-semibold text-slate-700">Lits occupés</span>
          </div>
          <div class="text-3xl font-semibold text-slate-900">{{ stats.patientsActifs }}</div>
          <p class="mt-1 text-sm text-slate-600">Séjours actifs</p>
          <RouterLink v-if="auth.canHospitalisation" to="/hospitalisations" class="mt-4 inline-flex text-sm font-semibold text-blue-600 hover:text-blue-700">
            Gérer les séjours →
          </RouterLink>
        </article>
      </div>
    </section>

    <section aria-label="Cas à surveiller">
      <article class="glass-card p-6">
        <div class="mb-4 flex items-center justify-between gap-3">
          <div>
            <h3 class="text-lg font-semibold text-white">Cas à surveiller</h3>
            <p class="text-sm text-slate-400">Alertes médicales prioritaires</p>
          </div>
          <RouterLink to="/hospitalisations" class="text-sm font-semibold text-sky-300 hover:text-sky-200">Voir tout →</RouterLink>
        </div>
        <div class="grid gap-3 md:grid-cols-2">
          <div
            v-for="cas in casSurveiller"
            :key="cas.patient_dossier + cas.motif"
            class="rounded-2xl border border-slate-600/50 bg-slate-900/50 p-4"
          >
            <div class="flex items-start justify-between gap-2">
              <strong class="text-white">{{ cas.patient_nom }}</strong>
              <span
                class="rounded-full px-2.5 py-1 text-xs font-bold uppercase"
                :class="cas.niveau === 'urgent' ? 'bg-orange-500/20 text-orange-200' : cas.niveau === 'attention' ? 'bg-amber-500/20 text-amber-200' : 'bg-emerald-500/20 text-emerald-200'"
              >
                {{ cas.niveau === 'urgent' ? 'Urgent' : cas.niveau === 'attention' ? 'Attention' : 'Stable' }}
              </span>
            </div>
            <p class="mt-2 text-sm text-slate-300">{{ cas.motif }}</p>
            <p class="mt-1 text-xs text-slate-500">{{ cas.patient_dossier }} · {{ cas.service }}</p>
          </div>
        </div>
      </article>
    </section>

    <section aria-label="Activité et tendances">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-6">
          <h3 class="text-lg font-semibold text-slate-900">Activité du jour</h3>
          <p class="mt-2 text-sm text-slate-500">Indicateurs consolidés</p>
        </div>
        <SimpleBarChart :series="activityChart" aria-label="Graphique activité du jour" />
      </article>
    </section>

    <section aria-label="Contact hospitalier">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div class="space-y-3">
            <h3 class="text-lg font-semibold text-slate-900">📍 Nous trouver</h3>
            <p class="text-sm font-semibold text-slate-700">Nkayi, Rue Houmba Makosso, Numéro 36</p>
            <p class="text-sm text-slate-500">Accessible 24h/24 · Urgences permanentes</p>
          </div>
          <div class="flex flex-wrap gap-3">
            <RouterLink to="/localisation" class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800">
              Voir la carte
            </RouterLink>
            <a
              class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              href="https://www.google.com/maps/dir/?api=1&destination=-4.2839,12.9860&travelmode=driving"
              target="_blank"
              rel="noreferrer noopener"
            >
              Itinéraire
            </a>
          </div>
        </div>
      </article>
    </section>

    <section v-for="category in moduleCategories" :key="category.id" class="space-y-4">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h3 class="text-lg font-semibold text-slate-900">{{ category.label }}</h3>
          <p class="text-sm text-slate-500">Accès rapide aux modules</p>
        </div>
      </div>
      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <RouterLink
          v-for="mod in category.modules"
          :key="mod.to"
          :to="mod.to"
          class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          :class="{ 'opacity-70': mod.placeholder }"
        >
          <div class="text-2xl">{{ getModuleIcon(mod.label) }}</div>
          <span class="mt-4 block text-sm font-semibold text-slate-900">{{ mod.label }}</span>
          <span v-if="mod.placeholder" class="mt-3 inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Bientôt</span>
        </RouterLink>
      </div>
    </section>

    <section v-if="auth.canHospitalisation" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 class="text-lg font-semibold text-slate-900">Hospitalisations en cours</h3>
          <p class="text-sm text-slate-500">Synthèse des séjours actifs</p>
        </div>
        <RouterLink to="/hospitalisations" class="inline-flex text-sm font-semibold text-blue-600 hover:text-blue-700">Tout voir →</RouterLink>
      </div>
      <div v-if="loading" class="rounded-3xl border border-slate-200 bg-slate-50 px-5 py-8 text-sm text-slate-600 text-center">
        Chargement des données…
      </div>
      <div v-else-if="hospitalisations.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-5 py-8 text-sm text-slate-600 text-center">
        Aucune hospitalisation active pour le moment.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-slate-500">
            <tr>
              <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Patient</th>
              <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Dossier</th>
              <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Localisation</th>
              <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Motif</th>
              <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Durée</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 bg-white">
            <tr v-for="h in hospitalisations" :key="h.id" class="hover:bg-slate-50">
              <td class="px-4 py-4 text-slate-700"><strong>{{ h.patient_prenom }} {{ h.patient_nom }}</strong></td>
              <td class="px-4 py-4 text-slate-700"><span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">{{ h.numero_dossier }}</span></td>
              <td class="px-4 py-4 text-slate-700">{{ h.batiment_code }}/{{ h.service_code }} · Ch.{{ h.chambre_numero }}</td>
              <td class="px-4 py-4 text-slate-700">{{ h.motif_admission }}</td>
              <td class="px-4 py-4 text-slate-700">~5 jours</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import SimpleBarChart from '../components/SimpleBarChart.vue'
import api, { getErrorMessage, unwrapList } from '../api/client.js'
import { useNavigation } from '../composables/useNavigation.js'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const { modulesByCategory: moduleCategories } = useNavigation()
const loading = ref(true)
const error = ref('')
const hospitalisations = ref([])
const casSurveiller = ref([])
const stats = reactive({
  patientsActifs: 0,
  rdvToday: 0,
  rdvPlanifies: 0,
  prescriptionsPending: 0,
  facturesEnAttente: 0,
  messagesNonLus: 0,
})

const todayLabel = computed(() => {
  return new Date().toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  })
})

const activityChart = computed(() => [
  { label: 'Patients', value: stats.patientsActifs, color: '#38bdf8' },
  { label: 'RDV jour', value: stats.rdvToday, color: '#a78bfa' },
  { label: 'Factures', value: stats.facturesEnAttente, color: '#fbbf24' },
  { label: 'Ordonn.', value: stats.prescriptionsPending, color: '#34d399' },
])

function getModuleIcon(label) {
  const icons = {
    'Patients': '👤',
    'Rendez-vous': '📅',
    'Prescriptions': '💊',
    'Hospitalisations': '🛏️',
    'Statistiques & Rapports': '📊',
    'Pharmacie': '⚕️',
    'Soins infirmiers': '🩹',
    'Documents médicaux': '📄',
    'Assurance & Mutuelles': '🛡️',
    'Services médicaux': '🏥',
    'Personnel — Médecins': '👨‍⚕️',
    'Personnel — Infirmiers': '👩‍⚕️',
    'Contact & Localisation': '📍',
    'Notifications': '🔔',
    'Urgences': '🚨',
    'Téléconsultation': '📱',
    'Inventaire': '📦',
    'Formation & RH': '📚',
    'Paramètres': '⚙️',
  }
  return icons[label] || '📌'
}

async function load() {
  loading.value = true
  error.value = ''
  hospitalisations.value = []
  try {
    const requests = [
      api.get('/dashboard/stats/'),
      api.get('/dashboard/cas-a-surveiller/'),
    ]
    if (auth.canHospitalisation) {
      requests.push(api.get('/hospitalisations/actives/'))
    }
    const results = await Promise.all(requests)
    const statsRes = results[0]
    casSurveiller.value = results[1].data
    stats.patientsActifs = statsRes.data.patients_actifs
    stats.rdvToday = statsRes.data.rdv_aujourdhui
    stats.rdvPlanifies = statsRes.data.rdv_planifies ?? 0
    stats.prescriptionsPending = statsRes.data.prescriptions_en_attente
    stats.facturesEnAttente = statsRes.data.factures_en_attente ?? 0
    stats.messagesNonLus = statsRes.data.messages_non_lus ?? 0
    if (auth.canHospitalisation && results[2]) {
      hospitalisations.value = unwrapList(results[2].data)
    }
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
