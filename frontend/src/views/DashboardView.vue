<template>
  <div class="tech-dashboard admin-dash">
    <a href="#main-staff" class="skip-link">Aller au contenu principal</a>

    <header class="dash-hero glass-card">
      <div class="dash-hero-brand">
        <div class="dash-logo" aria-hidden="true">+</div>
        <div>
          <p class="dash-kicker">SGHL Healthcare Management</p>
          <h1>Bienvenue, {{ roleWelcome }} !</h1>
          <p class="dash-sub">{{ todayLabel }} · Vue {{ auth.isAdmin ? 'administration' : 'opérationnelle' }}</p>
        </div>
      </div>
      <div class="dash-hero-actions">
        <RouterLink to="/notifications" class="icon-chip" title="Notifications">
          <span aria-hidden="true">🔔</span>
          <em v-if="notificationCount">{{ notificationCount }}</em>
        </RouterLink>
        <RouterLink to="/messagerie" class="icon-chip icon-chip--msg" title="Messages">
          <span aria-hidden="true">✉️</span>
          <em v-if="stats.messagesNonLus">{{ stats.messagesNonLus }}</em>
        </RouterLink>
        <RouterLink to="/profil" class="profile-chip">
          <span class="avatar">{{ initials }}</span>
          <span>{{ auth.fullName || 'Profil' }}</span>
        </RouterLink>
        <RouterLink v-if="auth.isAdmin" to="/parametres" class="icon-chip" title="Paramètres">⚙️</RouterLink>
      </div>
    </header>

    <div v-if="error" class="dash-error">{{ error }}</div>

    <section id="main-staff" class="kpi-grid" aria-label="Indicateurs clés">
      <article v-for="kpi in kpis" :key="kpi.label" class="kpi-card kpi-glow glass-card">
        <div class="kpi-head">
          <span class="kpi-icon" :style="{ background: kpi.tone }">{{ kpi.icon }}</span>
          <span>{{ kpi.label }}</span>
        </div>
        <div class="kpi-value">{{ loading ? '…' : kpi.value }}</div>
        <p>{{ kpi.hint }}</p>
        <RouterLink v-if="kpi.to" :to="kpi.to" class="kpi-link">Ouvrir →</RouterLink>
      </article>
    </section>

    <section class="charts-grid" aria-label="Visualisations">
      <article class="glass-card panel">
        <h3>Rendez-vous par service</h3>
        <p class="panel-sub">Répartition sur 30 jours</p>
        <SimpleDonutChart :series="rdvParService" />
      </article>

      <article v-if="showFinance" class="glass-card panel">
        <h3>Paiements mensuels</h3>
        <p class="panel-sub">Encaissements (FCFA)</p>
        <SimpleBarChart :series="paiementsMensuels" aria-label="Paiements mensuels" />
      </article>

      <article v-if="auth.isAdmin" class="glass-card panel">
        <h3>Activité du personnel</h3>
        <p class="panel-sub">7 derniers jours</p>
        <SimpleLineChart
          :labels="activitePersonnel.labels"
          :series="activitePersonnel.series"
          aria-label="Activité du personnel"
        />
      </article>

      <article v-else class="glass-card panel">
        <h3>Activité du jour</h3>
        <p class="panel-sub">Indicateurs consolidés</p>
        <SimpleBarChart :series="activityChart" aria-label="Activité du jour" />
      </article>

      <article class="glass-card panel panel--notifs">
        <div class="panel-head">
          <div>
            <h3>Notifications</h3>
            <p class="panel-sub">Alertes récentes</p>
          </div>
          <RouterLink to="/notifications">Tout voir →</RouterLink>
        </div>
        <ul v-if="notifications.length" class="feed-list">
          <li v-for="n in notifications" :key="n.id">
            <strong>{{ n.titre }}</strong>
            <span>{{ n.corps }}</span>
            <small>{{ relativeTime(n.created_at) }}</small>
          </li>
        </ul>
        <p v-else class="empty">Aucune notification récente.</p>
      </article>
    </section>

    <section class="manage-grid" aria-label="Gestion quotidienne">
      <article v-if="auth.isAdmin" class="glass-card panel">
        <div class="panel-head">
          <div>
            <h3>Derniers comptes</h3>
            <p class="panel-sub">Inscriptions récentes</p>
          </div>
          <RouterLink to="/comptes">Gérer →</RouterLink>
        </div>
        <ul class="account-list">
          <li v-for="compte in derniersComptes" :key="compte.id">
            <span class="avatar">{{ initialsOf(compte.full_name) }}</span>
            <div>
              <strong>{{ compte.full_name }}</strong>
              <span>{{ compte.role_label }}</span>
            </div>
            <small>{{ relativeTime(compte.date_joined) }}</small>
          </li>
        </ul>
        <p v-if="!derniersComptes.length" class="empty">Aucun compte récent.</p>
      </article>

      <article v-if="auth.canRdv" class="glass-card panel">
        <div class="panel-head">
          <div>
            <h3>Rendez-vous à valider</h3>
            <p class="panel-sub">En attente de confirmation</p>
          </div>
          <RouterLink to="/rendez-vous">Planning →</RouterLink>
        </div>
        <ul class="rdv-list">
          <li v-for="rdv in rdvAValider" :key="rdv.id">
            <div>
              <strong>{{ rdv.patient_nom }}</strong>
              <span>{{ formatTime(rdv.date_heure) }} · {{ rdv.motif }}</span>
            </div>
            <span class="badge-pending">En attente</span>
          </li>
        </ul>
        <p v-if="!rdvAValider.length" class="empty">Aucun rendez-vous en attente.</p>
      </article>

      <article class="glass-card panel shortcuts-panel">
        <h3>Raccourcis rapides</h3>
        <p class="panel-sub">Actions prioritaires</p>
        <div class="shortcut-stack">
          <RouterLink
            v-for="action in quickActions"
            :key="action.to + action.label"
            :to="action.to"
            class="shortcut-btn"
            :class="action.variant"
          >
            {{ action.label }}
          </RouterLink>
        </div>

        <div class="messages-block">
          <h4>Messages du jour</h4>
          <ul v-if="messagesDuJour.length" class="feed-list">
            <li v-for="msg in messagesDuJour" :key="msg.id">
              <strong>{{ msg.expediteur }}</strong>
              <span>{{ msg.sujet }}</span>
            </li>
          </ul>
          <p v-else class="empty">Pas de message aujourd’hui.</p>
          <RouterLink to="/messagerie" class="kpi-link">Ouvrir la messagerie →</RouterLink>
        </div>
      </article>
    </section>

    <section v-if="casSurveiller.length" class="glass-card panel" aria-label="Cas à surveiller">
      <div class="panel-head">
        <div>
          <h3>Cas à surveiller</h3>
          <p class="panel-sub">Alertes médicales prioritaires</p>
        </div>
        <RouterLink v-if="auth.canHospitalisation" to="/hospitalisations">Séjours →</RouterLink>
      </div>
      <div class="cas-grid">
        <div v-for="cas in casSurveiller" :key="cas.patient_dossier + cas.motif" class="cas-card">
          <div class="cas-top">
            <strong>{{ cas.patient_nom }}</strong>
            <span :class="['niveau', cas.niveau]">{{ niveauLabel(cas.niveau) }}</span>
          </div>
          <p>{{ cas.motif }}</p>
          <small>{{ cas.patient_dossier }} · {{ cas.service }}</small>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import SimpleBarChart from '../components/SimpleBarChart.vue'
import SimpleDonutChart from '../components/SimpleDonutChart.vue'
import SimpleLineChart from '../components/SimpleLineChart.vue'
import api, { getErrorMessage } from '../api/client.js'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const loading = ref(true)
const error = ref('')
const notificationCount = ref(0)
const rdvParService = ref([])
const paiementsMensuels = ref([])
const activitePersonnel = reactive({ labels: [], series: [] })
const derniersComptes = ref([])
const rdvAValider = ref([])
const notifications = ref([])
const messagesDuJour = ref([])
const casSurveiller = ref([])

const stats = reactive({
  utilisateursActifs: 0,
  patientsActifs: 0,
  rdvToday: 0,
  prescriptionsPending: 0,
  facturesEnAttente: 0,
  messagesNonLus: 0,
})

const roleLabels = {
  admin: 'Administrateur',
  medecin: 'Docteur',
  infirmier: 'Infirmier(ère)',
  biologiste: 'Biologiste',
  pharmacien: 'Pharmacien',
  comptable: 'Comptable',
  secretaire: 'Secrétaire',
}

const roleWelcome = computed(() => roleLabels[auth.role] || auth.fullName || 'équipe')
const showFinance = computed(() => auth.isAdmin || auth.role === 'comptable')

const todayLabel = computed(() =>
  new Date().toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  }),
)

const initials = computed(() => initialsOf(auth.fullName || auth.user?.username || 'U'))

const kpis = computed(() => {
  if (auth.isAdmin) {
    return [
      {
        label: 'Utilisateurs actifs',
        value: stats.utilisateursActifs,
        hint: 'Comptes actifs sur la plateforme',
        icon: '👤',
        tone: 'rgba(56,189,248,.18)',
        to: '/comptes',
      },
      {
        label: "Rendez-vous aujourd'hui",
        value: stats.rdvToday,
        hint: 'Planifiés ou confirmés',
        icon: '📅',
        tone: 'rgba(248,113,113,.18)',
        to: '/rendez-vous',
      },
      {
        label: 'Factures en attente',
        value: stats.facturesEnAttente,
        hint: 'À encaisser',
        icon: '🧾',
        tone: 'rgba(251,191,36,.18)',
        to: '/facturation',
      },
      {
        label: 'Messages non lus',
        value: stats.messagesNonLus,
        hint: 'Messagerie interne',
        icon: '✉️',
        tone: 'rgba(56,189,248,.18)',
        to: '/messagerie',
      },
    ]
  }

  const clinical = [
    {
      label: 'Patients actifs',
      value: stats.patientsActifs,
      hint: 'Hospitalisations en cours',
      icon: '👤',
      tone: 'rgba(56,189,248,.18)',
      to: auth.canHospitalisation ? '/hospitalisations' : null,
    },
    {
      label: "Rendez-vous aujourd'hui",
      value: stats.rdvToday,
      hint: 'Planning du jour',
      icon: '📅',
      tone: 'rgba(248,113,113,.18)',
      to: auth.canRdvRead ? '/rendez-vous' : null,
    },
  ]

  if (auth.canPrescriptionsRead) {
    clinical.push({
      label: 'Prescriptions en attente',
      value: stats.prescriptionsPending,
      hint: 'À valider / délivrer',
      icon: '💊',
      tone: 'rgba(167,139,250,.18)',
      to: '/prescriptions',
    })
  } else if (auth.canFacturationRead || auth.canCaisse) {
    clinical.push({
      label: 'Factures en attente',
      value: stats.facturesEnAttente,
      hint: 'À encaisser',
      icon: '🧾',
      tone: 'rgba(251,191,36,.18)',
      to: '/facturation',
    })
  }

  clinical.push({
    label: 'Messages non lus',
    value: stats.messagesNonLus,
    hint: 'Messagerie interne',
    icon: '✉️',
    tone: 'rgba(56,189,248,.18)',
    to: '/messagerie',
  })

  return clinical
})

const activityChart = computed(() => [
  { label: 'Patients', value: stats.patientsActifs, color: '#38bdf8' },
  { label: 'RDV', value: stats.rdvToday, color: '#a78bfa' },
  { label: 'Factures', value: stats.facturesEnAttente, color: '#fbbf24' },
  { label: 'Ordonn.', value: stats.prescriptionsPending, color: '#34d399' },
])

const quickActions = computed(() => {
  if (auth.isAdmin) {
    return [
      { label: 'Créer un compte', to: '/comptes?nouveau=1', variant: 'primary' },
      { label: 'Ajouter médecin', to: '/comptes?nouveau=1&role=medecin', variant: 'accent' },
      { label: 'Générer rapport', to: '/statistiques', variant: 'soft' },
    ]
  }
  const actions = []
  if (auth.canRdv) actions.push({ label: 'Nouveau rendez-vous', to: '/rendez-vous', variant: 'primary' })
  if (auth.canPatientsWrite) actions.push({ label: 'Fiches patients', to: '/patients', variant: 'accent' })
  if (auth.canCaisse) actions.push({ label: 'Ouvrir la caisse', to: '/caisse', variant: 'soft' })
  if (auth.canFacturationRead) actions.push({ label: 'Facturation', to: '/facturation', variant: 'soft' })
  if (auth.canLaboRead) actions.push({ label: 'Laboratoire', to: '/resultats-medicaux', variant: 'soft' })
  if (!actions.length) actions.push({ label: 'Messagerie', to: '/messagerie', variant: 'primary' })
  return actions.slice(0, 3)
})

function initialsOf(name) {
  return String(name || 'U')
    .split(/\s+/)
    .map((p) => p[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

function relativeTime(value) {
  if (!value) return ''
  const date = new Date(value)
  const diffMs = Date.now() - date.getTime()
  const mins = Math.round(diffMs / 60000)
  if (mins < 1) return "à l'instant"
  if (mins < 60) return `il y a ${mins} min`
  const hours = Math.round(mins / 60)
  if (hours < 24) return `il y a ${hours} h`
  const days = Math.round(hours / 24)
  return `il y a ${days} j`
}

function formatTime(value) {
  if (!value) return ''
  return new Date(value).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

function niveauLabel(niveau) {
  if (niveau === 'urgent') return 'Urgent'
  if (niveau === 'attention') return 'Attention'
  return 'Stable'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [overviewRes, notifRes] = await Promise.all([
      api.get('/dashboard/overview/'),
      api.get('/notifications/non-lues/').catch(() => ({ data: { count: 0 } })),
    ])
    const data = overviewRes.data
    notificationCount.value = notifRes.data?.count ?? 0
    stats.utilisateursActifs = data.kpis.utilisateurs_actifs
    stats.patientsActifs = data.kpis.patients_actifs
    stats.rdvToday = data.kpis.rdv_aujourdhui
    stats.prescriptionsPending = data.kpis.prescriptions_en_attente
    stats.facturesEnAttente = data.kpis.factures_en_attente
    stats.messagesNonLus = data.kpis.messages_non_lus
    rdvParService.value = data.rdv_par_service || []
    paiementsMensuels.value = data.paiements_mensuels || []
    activitePersonnel.labels = data.activite_personnel?.labels || []
    activitePersonnel.series = data.activite_personnel?.series || []
    derniersComptes.value = data.derniers_comptes || []
    rdvAValider.value = data.rdv_a_valider || []
    notifications.value = data.notifications || []
    messagesDuJour.value = data.messages_du_jour || []
    casSurveiller.value = data.cas_a_surveiller || []
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.admin-dash {
  display: grid;
  gap: 1.25rem;
}

.dash-hero {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.4rem;
}

.dash-hero-brand {
  display: flex;
  gap: 0.9rem;
  align-items: center;
}

.dash-logo {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.9rem;
  display: grid;
  place-items: center;
  font-size: 1.4rem;
  font-weight: 700;
  color: #0b1220;
  background: linear-gradient(135deg, #38bdf8, #34d399);
}

.dash-kicker {
  margin: 0;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #7dd3fc;
}

.dash-hero h1 {
  margin: 0.15rem 0;
  font-size: clamp(1.25rem, 2vw, 1.7rem);
  color: #f8fafc;
}

.dash-sub {
  margin: 0;
  color: #94a3b8;
  font-size: 0.85rem;
  text-transform: capitalize;
}

.dash-hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  align-items: center;
}

.icon-chip,
.profile-chip,
.shortcut-btn,
.kpi-link {
  text-decoration: none;
}

.icon-chip {
  position: relative;
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 0.8rem;
  display: grid;
  place-items: center;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(56, 189, 248, 0.25);
}

.icon-chip em {
  position: absolute;
  top: -0.35rem;
  right: -0.35rem;
  min-width: 1.1rem;
  height: 1.1rem;
  border-radius: 999px;
  background: #ef4444;
  color: white;
  font-size: 0.65rem;
  font-style: normal;
  display: grid;
  place-items: center;
  padding: 0 0.25rem;
}

.icon-chip--msg em {
  background: #0ea5e9;
}

.profile-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.7rem 0.35rem 0.35rem;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(56, 189, 248, 0.25);
  color: #e2e8f0;
  font-size: 0.85rem;
}

.avatar {
  width: 1.8rem;
  height: 1.8rem;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #38bdf8, #a78bfa);
  color: #0b1220;
  font-size: 0.7rem;
  font-weight: 700;
}

.dash-error {
  border-radius: 1rem;
  border: 1px solid rgba(244, 63, 94, 0.4);
  background: rgba(127, 29, 29, 0.35);
  color: #fecdd3;
  padding: 0.85rem 1rem;
}

.kpi-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.kpi-card {
  padding: 1rem 1.1rem;
}

.kpi-head {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  color: #cbd5e1;
  font-size: 0.88rem;
  font-weight: 600;
}

.kpi-icon {
  width: 2.3rem;
  height: 2.3rem;
  border-radius: 0.75rem;
  display: grid;
  place-items: center;
}

.kpi-value {
  margin-top: 0.7rem;
  font-size: 2rem;
  font-weight: 700;
  color: #f8fafc;
}

.kpi-card p {
  margin: 0.2rem 0 0;
  color: #94a3b8;
  font-size: 0.8rem;
}

.kpi-link {
  display: inline-flex;
  margin-top: 0.7rem;
  color: #7dd3fc;
  font-size: 0.82rem;
  font-weight: 600;
}

.charts-grid,
.manage-grid {
  display: grid;
  gap: 1rem;
}

@media (min-width: 960px) {
  .charts-grid {
    grid-template-columns: 1.1fr 1.1fr 1.1fr 0.9fr;
  }

  .manage-grid {
    grid-template-columns: 1.2fr 1.2fr 0.9fr;
  }
}

.panel {
  padding: 1.1rem 1.2rem;
}

.panel h3,
.panel h4 {
  margin: 0;
  color: #f1f5f9;
}

.panel-sub {
  margin: 0.25rem 0 1rem;
  color: #94a3b8;
  font-size: 0.8rem;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.panel-head a,
.messages-block .kpi-link {
  color: #7dd3fc;
  font-size: 0.82rem;
  font-weight: 600;
  white-space: nowrap;
}

.feed-list,
.account-list,
.rdv-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.7rem;
}

.feed-list li,
.account-list li,
.rdv-list li {
  display: grid;
  gap: 0.15rem;
  padding: 0.65rem 0.7rem;
  border-radius: 0.85rem;
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.feed-list strong,
.account-list strong,
.rdv-list strong {
  color: #f8fafc;
  font-size: 0.88rem;
}

.feed-list span,
.account-list span,
.rdv-list span {
  color: #94a3b8;
  font-size: 0.78rem;
}

.feed-list small,
.account-list small {
  color: #64748b;
  font-size: 0.72rem;
}

.account-list li,
.rdv-list li {
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.65rem;
}

.rdv-list li {
  grid-template-columns: 1fr auto;
}

.badge-pending {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.25rem 0.65rem;
  background: rgba(45, 212, 191, 0.18);
  color: #5eead4;
  font-size: 0.72rem;
  font-weight: 700;
}

.shortcut-stack {
  display: grid;
  gap: 0.55rem;
}

.shortcut-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 2.6rem;
  border-radius: 0.85rem;
  font-size: 0.88rem;
  font-weight: 700;
  color: #0b1220;
  transition: transform 0.15s ease, filter 0.15s ease;
}

.shortcut-btn:hover {
  transform: translateY(-1px);
  filter: brightness(1.05);
}

.shortcut-btn.primary {
  background: linear-gradient(135deg, #2dd4bf, #38bdf8);
}

.shortcut-btn.accent {
  background: linear-gradient(135deg, #38bdf8, #818cf8);
}

.shortcut-btn.soft {
  background: rgba(148, 163, 184, 0.18);
  color: #e2e8f0;
  border: 1px solid rgba(148, 163, 184, 0.25);
}

.messages-block {
  margin-top: 1.1rem;
  padding-top: 0.9rem;
  border-top: 1px solid rgba(148, 163, 184, 0.15);
}

.messages-block h4 {
  margin-bottom: 0.65rem;
  font-size: 0.92rem;
}

.empty {
  margin: 0;
  color: #64748b;
  font-size: 0.85rem;
}

.cas-grid {
  display: grid;
  gap: 0.75rem;
}

@media (min-width: 720px) {
  .cas-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.cas-card {
  padding: 0.85rem;
  border-radius: 0.9rem;
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.cas-top {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  align-items: center;
}

.cas-card p {
  margin: 0.45rem 0 0.25rem;
  color: #cbd5e1;
  font-size: 0.85rem;
}

.cas-card small {
  color: #64748b;
}

.niveau {
  border-radius: 999px;
  padding: 0.2rem 0.55rem;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
}

.niveau.urgent {
  background: rgba(249, 115, 22, 0.2);
  color: #fdba74;
}

.niveau.attention {
  background: rgba(251, 191, 36, 0.2);
  color: #fde68a;
}

.niveau.stable {
  background: rgba(52, 211, 153, 0.2);
  color: #6ee7b7;
}
</style>
