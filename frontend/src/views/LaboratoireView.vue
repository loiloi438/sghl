<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Résultats médicaux</h1>
            <p class="mt-1 text-sm text-slate-600">Laboratoire (LIS) — commandes, prélèvements et publication</p>
          </div>
          <button class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" type="button" @click="loadBase">Actualiser</button>
        </div>
      </div>

      <div v-if="message" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
      <div v-if="error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <label class="mb-2 block text-sm font-medium text-slate-700" for="hospitalisation">Hospitalisation</label>
        <select id="hospitalisation" v-model="selectedHospId" @change="onHospChange" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500 md:max-w-md">
          <option value="">— Sélectionner —</option>
          <option v-for="h in hospitalisations" :key="h.id" :value="h.id">{{ h.numero_dossier }} — {{ h.patient_prenom }} {{ h.patient_nom }}</option>
        </select>
      </div>

      <div v-if="selectedHospId && auth.canLaboCommande" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Nouvelle commande d'analyses</h2>
        <form class="mt-5 space-y-4" @submit.prevent="createCommande">
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Analyses</label>
            <select v-model="form.codes_analyses" multiple size="5" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500">
              <option v-for="a in analyses" :key="a.code" :value="a.code">{{ a.code }} — {{ a.libelle }}</option>
            </select>
          </div>
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">Observations</label>
            <textarea v-model="form.observations" class="min-h-[120px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
          </div>
          <button class="rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700" type="submit">Commander</button>
        </form>
      </div>

      <div v-if="selectedCommande" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Commande — {{ statutLabel(selectedCommande.statut) }}</h2>
            <p class="mt-2 text-sm text-slate-500">v{{ selectedCommande.version }} · {{ selectedCommande.observations || 'Sans observation' }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <button v-if="selectedCommande.statut === 'commandee' && canPrelever" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" @click="prelever">Enregistrer prélèvement</button>
            <button v-if="selectedCommande.statut === 'prelevee' && auth.canLabo" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" @click="affecter">Affecter au biologiste</button>
            <button v-if="['affectee', 'resultats_saisis'].includes(selectedCommande.statut) && auth.canLabo" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" @click="saisirResultats">Saisir résultats</button>
            <button v-if="selectedCommande.statut === 'resultats_saisis' && auth.canLabo" class="rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700" @click="valider">Valider (biologiste)</button>
            <button v-if="selectedCommande.statut === 'validee' && auth.canLabo" class="rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700" @click="publier">Publier au patient</button>
            <button v-if="selectedCommande.statut === 'publiee'" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" @click="telechargerPdf">PDF signé</button>
          </div>
        </div>
        <ul class="mt-6 space-y-3 rounded-3xl border border-slate-200 bg-slate-50 p-4">
          <li v-for="l in selectedCommande.lignes" :key="l.id" class="flex flex-col gap-2 rounded-2xl bg-white p-4 shadow-sm">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <strong class="text-slate-900">{{ l.code_analyse }}</strong>
              <span class="text-sm text-slate-500">{{ l.libelle }}</span>
            </div>
            <p class="text-sm text-slate-700">
              <span v-if="l.resultat">Résultat → {{ l.resultat.valeur }} {{ l.resultat.unite }}</span>
              <span v-else-if="needsResultInput(l)" class="text-slate-500 italic">en attente</span>
              <span v-else class="text-slate-500">Sans résultat</span>
            </p>
          </li>
        </ul>
      </div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Commandes</h2>
        <div v-if="!selectedHospId" class="mt-4 text-sm text-slate-500">Sélectionnez une hospitalisation.</div>
        <div v-else-if="commandes.length === 0" class="mt-4 text-sm text-slate-500">Aucune commande.</div>
        <div v-else class="mt-4 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Statut</th>
                <th class="px-3 py-3 font-medium">Analyses</th>
                <th class="px-3 py-3 font-medium">Créée le</th>
                <th class="px-3 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="c in commandes" :key="c.id" class="hover:bg-slate-50">
                <td class="px-3 py-3"><span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600">{{ statutLabel(c.statut) }}</span></td>
                <td class="px-3 py-3 text-slate-700">{{ c.lignes?.map((l) => l.code_analyse).join(', ') }}</td>
                <td class="px-3 py-3 text-slate-700">{{ formatDate(c.created_at) }}</td>
                <td class="px-3 py-3">
                  <button class="rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" @click="selectCommande(c.id)">Ouvrir</button>
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
import api, { downloadPdf, getErrorMessage, unwrapList } from '../api/client.js'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const hospitalisations = ref([])
const analyses = ref([])
const commandes = ref([])
const selectedHospId = ref('')
const selectedCommande = ref(null)
const error = ref('')
const message = ref('')

const form = reactive({ codes_analyses: [], observations: '' })

const canPrelever = computed(() => auth.canLaboPrelever)

const statutLabels = {
  commandee: 'Commandée',
  prelevee: 'Prélevée',
  affectee: 'Affectée',
  resultats_saisis: 'Résultats saisis',
  validee: 'Validée',
  publiee: 'Publiée',
}

function statutLabel(s) {
  return statutLabels[s] || s
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('fr-FR')
  } catch {
    return iso
  }
}

function needsResultInput(ligne) {
  return selectedCommande.value?.statut === 'affectee' && !ligne.resultat
}

async function loadBase() {
  error.value = ''
  const anaRes = await api.get('/analyses-catalogue/')
  analyses.value = unwrapList(anaRes.data)
  if (!auth.canHospitalisation) {
    error.value = 'Liste des séjours non disponible pour votre rôle.'
    return
  }
  const hospRes = await api.get('/hospitalisations/actives/')
  hospitalisations.value = unwrapList(hospRes.data)
  if (hospitalisations.value.length && !selectedHospId.value) {
    selectedHospId.value = hospitalisations.value[0].id
    await loadCommandes()
  }
}

async function loadCommandes() {
  if (!selectedHospId.value) return
  const { data } = await api.get(`/hospitalisations/${selectedHospId.value}/commandes-analyses/`)
  commandes.value = unwrapList(data)
}

async function selectCommande(id) {
  const { data } = await api.get(`/commandes-analyses/${id}/`)
  selectedCommande.value = data
}

async function onHospChange() {
  selectedCommande.value = null
  await loadCommandes()
}

async function createCommande() {
  error.value = ''
  message.value = ''
  try {
    await api.post(`/hospitalisations/${selectedHospId.value}/commandes-analyses/`, form)
    message.value = 'Commande créée.'
    form.codes_analyses = []
    form.observations = ''
    await loadCommandes()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function prelever() {
  error.value = ''
  try {
    const { data } = await api.post(`/commandes-analyses/${selectedCommande.value.id}/prelevement/`, {
      type_echantillon: 'Sang veineux',
      reference_echantillon: `WEB-${Date.now()}`,
    })
    selectedCommande.value = data
    message.value = 'Prélèvement enregistré.'
    await loadCommandes()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function affecter() {
  error.value = ''
  try {
    const { data } = await api.post(`/commandes-analyses/${selectedCommande.value.id}/affectation/`, {
      affectee_a_id: auth.user.id,
    })
    selectedCommande.value = data
    message.value = 'Commande affectée.'
    await loadCommandes()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function saisirResultats() {
  const resultats = selectedCommande.value.lignes.map((l) => {
    const valeur = prompt(`${l.code_analyse} — ${l.libelle}\nSaisir la valeur :`, l.resultat?.valeur || '')
    if (valeur === null) return null
    return { ligne_id: l.id, valeur, unite: l.unite_reference || '' }
  }).filter(Boolean)

  if (resultats.length !== selectedCommande.value.lignes.length) return

  error.value = ''
  try {
    const { data } = await api.post(`/commandes-analyses/${selectedCommande.value.id}/resultats/`, {
      resultats,
    })
    selectedCommande.value = data
    message.value = 'Résultats enregistrés.'
    await loadCommandes()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function valider() {
  error.value = ''
  try {
    const { data } = await api.post(`/commandes-analyses/${selectedCommande.value.id}/valider/`, {
      version: selectedCommande.value.version,
    })
    selectedCommande.value = data
    message.value = 'Résultats validés (immuables).'
    await loadCommandes()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function publier() {
  error.value = ''
  try {
    const { data } = await api.post(`/commandes-analyses/${selectedCommande.value.id}/publier/`, {
      version: selectedCommande.value.version,
    })
    selectedCommande.value = data
    message.value = 'Résultats publiés — visibles par le patient.'
    await loadCommandes()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function telechargerPdf() {
  if (!selectedCommande.value) return
  error.value = ''
  try {
    await downloadPdf(
      `/commandes-analyses/${selectedCommande.value.id}/pdf/`,
      `labo-${selectedCommande.value.id}.pdf`,
    )
    message.value = 'Compte-rendu PDF téléchargé.'
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

