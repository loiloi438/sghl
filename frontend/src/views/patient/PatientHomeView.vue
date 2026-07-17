<template>
  <div class="hc-page">
    <a href="#main-patient" class="skip-link">Aller au contenu principal</a>

    <section class="hc-hero hc-hero--photo">
      <div>
        <p class="hc-hero-tag">🌿 Human-Care · Pour votre santé et bien-être</p>
        <h1 class="hc-hero-title">
          Bienvenue{{ profil ? `, ${profil.prenom}` : '' }} !
        </h1>
        <p class="hc-hero-sub">Votre espace patient SGHL — simple, rassurant et sécurisé.</p>
      </div>
      <PatientHeroIllustration />
    </section>

    <div v-if="error" class="hc-alert hc-alert--error">{{ error }}</div>
    <div v-if="loading" class="hc-loading">Chargement de votre tableau de bord…</div>

    <template v-else-if="dashboard">
      <section id="main-patient" class="hc-summary-row">
        <article class="hc-summary-chip">
          <span class="hc-summary-label">Rendez-vous à venir</span>
          <strong class="hc-summary-value">{{ rdvCount }}</strong>
        </article>
        <article class="hc-summary-chip">
          <span class="hc-summary-label">Ordonnances actives</span>
          <strong class="hc-summary-value">{{ prescriptionsActives }}</strong>
        </article>
        <article class="hc-summary-chip hc-summary-chip--warn" v-if="facturePending">
          <span class="hc-summary-label">Factures</span>
          <strong class="hc-summary-value">1 en attente</strong>
        </article>
        <article class="hc-summary-chip" v-else>
          <span class="hc-summary-label">Factures</span>
          <strong class="hc-summary-value">À jour</strong>
        </article>
      </section>

      <section class="hc-empathy-banner">
        <div>
          <h2>{{ dashboard.message_bienveillance || 'Vous êtes entre de bonnes mains 💙' }}</h2>
          <p>Prenez soin de vous{{ profil ? `, ${profil.prenom}` : '' }} !</p>
        </div>
        <img
          src="/images/visitor/equipe.jpg"
          alt="Équipe soignante SGHL"
          width="200"
          height="160"
          loading="lazy"
        />
      </section>

      <section class="hc-widget-grid">
        <article class="hc-widget hc-widget--photo">
          <div class="hc-widget-media">
            <img src="/images/visitor/infra.jpg" alt="" width="320" height="140" loading="lazy" />
          </div>
          <h3>Prochain rendez-vous</h3>
          <template v-if="prochainRdv">
            <p class="hc-widget-title">{{ prochainRdv.motif || 'Consultation' }}</p>
            <p class="hc-widget-meta">{{ formatPatientDate(prochainRdv.date_heure) }}</p>
            <p class="hc-widget-meta">
              {{ prochainRdv.medecin_nom }} · {{ rdvStatutLabel(prochainRdv.statut) }}
            </p>
            <div class="hc-widget-actions">
              <RouterLink to="/patient/rendez-vous" class="hc-btn-rdv a11y-touch">Voir mes RDV</RouterLink>
            </div>
          </template>
          <template v-else>
            <p class="hc-widget-meta">Aucun rendez-vous prévu pour le moment.</p>
            <div class="hc-widget-actions">
              <RouterLink to="/patient/rendez-vous" class="hc-btn-rdv a11y-touch">📅 Prendre rendez-vous</RouterLink>
            </div>
          </template>
        </article>

        <article class="hc-widget hc-widget--photo">
          <div class="hc-widget-media">
            <img src="/images/visitor/labo.jpg" alt="" width="320" height="140" loading="lazy" />
          </div>
          <h3>Mes analyses</h3>
          <template v-if="dernierLabo">
            <p class="hc-widget-title">{{ (dernierLabo.analyses || []).slice(0, 2).join(', ') || 'Résultat laboratoire' }}</p>
            <p class="hc-widget-meta">
              {{ formatPatientDateShort(dernierLabo.publiee_le) }}
              <span v-if="dernierLabo.statut"> · {{ dernierLabo.statut }}</span>
            </p>
            <div class="hc-widget-actions">
              <RouterLink to="/patient/laboratoire" class="hc-btn-secondary a11y-touch">Voir détails</RouterLink>
            </div>
          </template>
          <template v-else>
            <p class="hc-widget-meta">Vos résultats apparaîtront ici dès publication.</p>
            <div class="hc-widget-actions">
              <RouterLink to="/patient/laboratoire" class="hc-btn-secondary a11y-touch">Laboratoire</RouterLink>
            </div>
          </template>
        </article>

        <article class="hc-widget">
          <h3>Messages</h3>
          <ul v-if="messagesPreview.length" class="hc-msg-list">
            <li v-for="m in messagesPreview" :key="m.id">
              <strong>{{ m.expediteur_nom || 'SGHL' }}</strong>
              <span>{{ truncate(m.sujet || m.corps, 64) }}</span>
            </li>
          </ul>
          <p v-else class="hc-widget-meta">Aucun message récent.</p>
          <div class="hc-widget-actions">
            <RouterLink to="/patient/messages" class="hc-btn-secondary a11y-touch">Voir tous les messages</RouterLink>
          </div>
        </article>

        <article class="hc-widget hc-widget--photo">
          <div class="hc-widget-media">
            <img src="/images/visitor/secure.jpg" alt="" width="320" height="140" loading="lazy" />
          </div>
          <h3>Mes factures</h3>
          <template v-if="facturePending">
            <p class="hc-widget-title">Facture en attente</p>
            <p class="hc-widget-amount">{{ formatMontant(facturePending.montant_restant ?? facturePending.montant_total) }} FCFA</p>
            <p class="hc-widget-meta">{{ formatPatientDateShort(facturePending.validee_le || facturePending.payee_le) }}</p>
            <div class="hc-widget-actions">
              <RouterLink to="/patient/factures" class="hc-btn-pay a11y-touch">Régler maintenant</RouterLink>
            </div>
          </template>
          <template v-else>
            <p class="hc-widget-meta">Aucune facture en attente 💙</p>
            <div class="hc-widget-actions">
              <RouterLink to="/patient/factures" class="hc-btn-secondary a11y-touch">Voir mes factures</RouterLink>
            </div>
          </template>
        </article>
      </section>

      <section v-if="dashboard.hospitalisation_active" class="hc-card hc-card-padded">
        <h3 class="font-bold text-teal-900" style="font-family: Poppins, sans-serif">Votre séjour en cours</h3>
        <p class="mt-2 text-sm leading-relaxed text-slate-700">
          {{ dashboard.hospitalisation_active.motif_admission }}
        </p>
        <div class="mt-4 grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
          <p>
            <strong class="text-teal-800">Service :</strong>
            {{ dashboard.hospitalisation_active.service_nom || dashboard.hospitalisation_active.service_code }}
          </p>
          <p>
            <strong class="text-teal-800">Médecin référent :</strong>
            {{ dashboard.hospitalisation_active.medecin_nom || '—' }}
          </p>
          <p>
            <strong class="text-teal-800">Chambre :</strong>
            {{ dashboard.hospitalisation_active.chambre_numero }} · Lit {{ dashboard.hospitalisation_active.lit_numero }}
          </p>
          <p>
            <strong class="text-teal-800">Admission :</strong>
            {{ formatPatientDate(dashboard.hospitalisation_active.date_admission) }}
          </p>
        </div>
        <RouterLink to="/patient/hospitalisations" class="hc-btn-secondary mt-4 inline-flex">
          Voir mon historique →
        </RouterLink>
      </section>

      <section v-if="dashboard.prochaines_doses?.length">
        <h3 class="mb-3 text-sm font-bold uppercase tracking-widest text-teal-800">Prochains soins</h3>
        <div class="space-y-3">
          <article
            v-for="d in dashboard.prochaines_doses.slice(0, 3)"
            :key="d.id"
            class="hc-list-item"
          >
            <div class="flex flex-wrap items-center justify-between gap-2">
              <strong class="text-slate-900">{{ d.medicament }}</strong>
              <span class="hc-badge" :class="`hc-badge--${doseStatutMeta(d).badge}`">
                {{ doseStatutMeta(d).icon }} {{ doseStatutMeta(d).label }}
              </span>
            </div>
            <p class="mt-1 text-sm text-slate-600">{{ d.posologie }}</p>
            <p class="mt-2 text-xs text-slate-500">
              {{ formatPatientDate(d.heure_prevue) }}
              <span v-if="d.infirmier_nom"> · {{ d.infirmier_nom }}</span>
            </p>
          </article>
        </div>
      </section>

      <section class="hc-bottom-grid">
        <div>
          <h3 class="mb-3 text-sm font-bold uppercase tracking-widest text-teal-800">Conseils santé</h3>
          <div class="hc-tips-grid">
            <RouterLink
              v-for="post in healthTips"
              :key="post.slug"
              :to="`/blog/${post.slug}`"
              class="hc-tip-card"
            >
              <img :src="post.image" :alt="post.title" width="280" height="140" loading="lazy" />
              <span>{{ post.title }}</span>
            </RouterLink>
          </div>
        </div>
        <div>
          <h3 class="mb-3 text-sm font-bold uppercase tracking-widest text-teal-800">Historique des RDV</h3>
          <div class="hc-card hc-card-padded">
            <ul v-if="rdvHistorique.length" class="hc-history-list">
              <li v-for="r in rdvHistorique" :key="r.id">
                <span class="hc-history-check" aria-hidden="true">✓</span>
                <div>
                  <strong>{{ r.motif || 'Consultation' }}</strong>
                  <p>{{ formatPatientDateShort(r.date_heure) }} · {{ rdvStatutLabel(r.statut) }}</p>
                </div>
              </li>
            </ul>
            <p v-else class="hc-widget-meta">Vos rendez-vous passés apparaîtront ici.</p>
            <RouterLink to="/patient/rendez-vous" class="hc-btn-secondary mt-4 inline-flex a11y-touch">
              Voir l’historique complet
            </RouterLink>
          </div>
        </div>
      </section>

      <section>
        <h3 class="mb-3 text-sm font-bold uppercase tracking-widest text-teal-800">Accès rapide</h3>
        <div class="hc-shortcuts">
          <RouterLink v-for="card in shortcutCards" :key="card.to" :to="card.to" class="hc-shortcut a11y-touch">
            <span class="hc-shortcut-icon">{{ card.icon }}</span>
            <span class="hc-shortcut-label">{{ card.label }}</span>
            <span class="text-xs text-slate-500">{{ card.hint }}</span>
          </RouterLink>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api, { getErrorMessage } from '../../api/client.js'
import {
  doseStatutMeta,
  formatMontant,
  formatPatientDate,
  formatPatientDateShort,
  rdvStatutLabel,
} from '../../composables/usePatientPortal.js'
import { blogPosts } from '../../data/publicContent.js'
import PatientHeroIllustration from '../../components/patient/PatientHeroIllustration.vue'

const loading = ref(true)
const error = ref('')
const dashboard = ref(null)
const prescriptions = ref([])
const factures = ref([])
const labos = ref([])
const messages = ref([])
const allRdv = ref([])

const profil = computed(() => dashboard.value?.profil)
const rdvCount = computed(() => dashboard.value?.prochains_rdv?.length || 0)
const prochainRdv = computed(() => dashboard.value?.prochains_rdv?.[0] || null)

const prescriptionsActives = computed(() =>
  prescriptions.value.filter(
    (p) => p.statut === 'validee' || p.statut_pharmacie === 'validee' || p.statut_pharmacie === 'en_attente',
  ).length,
)

const facturePending = computed(() => {
  return (
    factures.value.find((f) => Number(f.montant_restant ?? 0) > 0) || null
  )
})

const dernierLabo = computed(() => labos.value[0] || null)
const messagesPreview = computed(() => messages.value.slice(0, 2))
const healthTips = blogPosts.filter((p) =>
  ['gestion-du-stress', 'prevention-diabete'].includes(p.slug),
)

const rdvHistorique = computed(() => {
  const past = allRdv.value.filter((r) => {
    const done = ['termine', 'annule', 'absent', 'confirme'].includes(r.statut)
    const isPast = r.date_heure && new Date(r.date_heure) < new Date()
    return done || isPast
  })
  return past.slice(0, 3)
})

const shortcutCards = [
  { to: '/patient/hospitalisations', label: 'Hospitalisation', icon: '🏥', hint: 'Historique & séjour' },
  { to: '/patient/prescriptions', label: 'Pharmacie', icon: '💊', hint: 'Ordonnances & retraits' },
  { to: '/patient/laboratoire', label: 'Laboratoire', icon: '🔬', hint: 'Analyses & courbes' },
  { to: '/patient/factures', label: 'Factures', icon: '🧾', hint: 'Paiements & reçus' },
]

function truncate(text, max) {
  const t = String(text || '').trim()
  if (t.length <= max) return t
  return `${t.slice(0, max - 1)}…`
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [dashRes, prescRes, factRes, labRes, msgRes, rdvRes] = await Promise.all([
      api.get('/patient/tableau-de-bord/'),
      api.get('/patient/prescriptions/').catch(() => ({ data: [] })),
      api.get('/patient/factures/').catch(() => ({ data: [] })),
      api.get('/patient/resultats-laboratoire/').catch(() => ({ data: [] })),
      api.get('/patient/messages/').catch(() => ({ data: [] })),
      api.get('/patient/rendez-vous/').catch(() => ({ data: [] })),
    ])
    dashboard.value = dashRes.data
    prescriptions.value = Array.isArray(prescRes.data) ? prescRes.data : []
    factures.value = Array.isArray(factRes.data) ? factRes.data : []
    labos.value = Array.isArray(labRes.data) ? labRes.data : []
    messages.value = Array.isArray(msgRes.data) ? msgRes.data : []
    allRdv.value = Array.isArray(rdvRes.data) ? rdvRes.data : []
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
