<template>

  <div class="hc-page">

    <a href="#main-patient" class="skip-link">Aller au contenu principal</a>



    <section class="hc-hero">

      <div>

        <p class="hc-hero-tag">🌿 Human-Care · Pour votre santé et bien-être</p>

        <h1 class="hc-hero-title">

          Bonjour{{ profil ? `, ${profil.prenom}` : '' }} 👋

        </h1>

        <p class="hc-hero-sub">Votre espace patient SGHL — simple, rassurant et sécurisé.</p>

        <p v-if="dashboard?.message_bienveillance" class="hc-wellness">

          {{ dashboard.message_bienveillance }}

        </p>

      </div>

      <PatientHeroIllustration />

    </section>



    <div v-if="error" class="hc-alert hc-alert--error">{{ error }}</div>

    <div v-if="loading" class="hc-loading">Chargement de votre tableau de bord…</div>



    <template v-else-if="dashboard">

      <section id="main-patient" class="hc-card hc-card-padded">

        <div class="hc-kpi-grid hc-kpi-grid--4">

          <PatientKpiCard

            label="Hospitalisation"

            :value="hospLabel"

            :detail="hospDetail"

            tone="sky"

            label-color="#0369a1"

          />

          <PatientKpiCard

            label="Doses à venir"

            :value="dosesCount"

            :detail="dosesDetail"

            tone="lavender"

            label-color="#6d28d9"

          />

          <PatientKpiCard

            label="Constantes récentes"

            :value="constantesCount"

            :detail="derniereConstante"

            tone="sand"

            label-color="#b45309"

          />

          <PatientKpiCard

            label="Rendez-vous"

            :value="rdvCount"

            :detail="prochainRdvDetail"

            tone="mint"

            label-color="#0d9488"

          />

        </div>



        <div class="mt-8 flex flex-wrap gap-3">

          <RouterLink to="/patient/rendez-vous" class="hc-btn-rdv a11y-touch">

            📅 Prendre rendez-vous

          </RouterLink>

          <RouterLink to="/patient/messages" class="hc-btn-secondary a11y-touch">

            💬 Contacter le secrétariat

          </RouterLink>

        </div>

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

  constanteSummary,

  doseStatutMeta,

  formatPatientDate,

  rdvStatutLabel,

} from '../../composables/usePatientPortal.js'

import PatientHeroIllustration from '../../components/patient/PatientHeroIllustration.vue'

import PatientKpiCard from '../../components/patient/PatientKpiCard.vue'



const loading = ref(true)

const error = ref('')

const dashboard = ref(null)



const profil = computed(() => dashboard.value?.profil)



const hospLabel = computed(() => {

  if (dashboard.value?.hospitalisation_active) return 'En cours'

  return 'Aucune en cours'

})



const hospDetail = computed(() => {

  if (dashboard.value?.hospitalisation_active) {

    return dashboard.value.hospitalisation_active.service_nom || 'Suivi actif'

  }

  return 'Vous êtes en bonne santé 💙'

})



const dosesCount = computed(() => dashboard.value?.prochaines_doses?.length || 0)

const dosesDetail = computed(() => {

  if (!dosesCount.value) return 'Rien de prévu pour l’instant'

  const next = dashboard.value.prochaines_doses[0]

  return `Prochaine : ${next.medicament}`

})



const constantesCount = computed(() => dashboard.value?.constantes_recentes?.length || 0)

const derniereConstante = computed(() => {

  const c = dashboard.value?.constantes_recentes?.[0]

  if (!c) return 'Vos constantes seront affichées ici'

  return constanteSummary(c)

})



const rdvCount = computed(() => dashboard.value?.prochains_rdv?.length || 0)

const prochainRdvDetail = computed(() => {

  const rdv = dashboard.value?.prochains_rdv?.[0]

  if (!rdv) return 'Planifiez votre prochaine visite'

  return `${formatPatientDate(rdv.date_heure)} · ${rdvStatutLabel(rdv.statut)}`

})



const shortcutCards = [

  { to: '/patient/hospitalisations', label: 'Hospitalisation', icon: '🏥', hint: 'Historique & séjour' },

  { to: '/patient/prescriptions', label: 'Pharmacie', icon: '💊', hint: 'Ordonnances & retraits' },

  { to: '/patient/laboratoire', label: 'Laboratoire', icon: '🔬', hint: 'Analyses & courbes' },

  { to: '/patient/factures', label: 'Factures', icon: '🧾', hint: 'Paiements & reçus' },

]



async function load() {

  loading.value = true

  error.value = ''

  try {

    const { data } = await api.get('/patient/tableau-de-bord/')

    dashboard.value = data

  } catch (e) {

    error.value = getErrorMessage(e)

  } finally {

    loading.value = false

  }

}



onMounted(load)

</script>


