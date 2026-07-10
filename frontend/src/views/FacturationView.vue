<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <div class="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Facturation</h1>
          <p class="mt-1 text-sm text-slate-600">Génération, validation et encaissement des factures</p>
        </div>
        <button class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" type="button" @click="loadAll">Actualiser</button>
      </div>

      <div v-if="message" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
      <div v-if="error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Hospitalisations à facturer</h2>
        <div v-if="!auth.canFacturation" class="mt-4 text-sm text-slate-600">
          {{
            auth.canFacturationRead
              ? 'Consultation des tarifs ci-dessous — encaissement réservé au comptable.'
              : 'Accès refusé.'
          }}
        </div>
        <div v-else-if="aFacturer.length === 0" class="mt-4 text-sm text-slate-600">Aucune hospitalisation à facturer.</div>
        <div v-else class="mt-4 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Patient</th>
                <th class="px-3 py-3 font-medium">Statut séjour</th>
                <th class="px-3 py-3 font-medium">Facture</th>
                <th class="px-3 py-3 font-medium">Montant</th>
                <th class="px-3 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="h in aFacturer" :key="h.hospitalisation_id" class="hover:bg-slate-50">
                <td class="px-3 py-3 text-slate-700">{{ h.patient_nom }} ({{ h.numero_dossier }})</td>
                <td class="px-3 py-3 text-slate-700">{{ h.statut_hospitalisation }}</td>
                <td class="px-3 py-3 text-slate-700">{{ h.facture_statut || '—' }}</td>
                <td class="px-3 py-3 text-slate-700">{{ formatMontant(h.montant_total) }}</td>
                <td class="px-3 py-3">
                  <div class="flex flex-wrap gap-2">
                    <button class="rounded-xl bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-700" @click="generer(h.hospitalisation_id)">
                      {{ h.facture_id ? 'Régénérer' : 'Générer' }}
                    </button>
                    <button
                      v-if="h.facture_id && h.facture_statut === 'brouillon'"
                      class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                      @click="ouvrirFacture(h.facture_id)"
                    >
                      Valider
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="factureCourante" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Facture — {{ factureCourante.patient_nom }}</h2>
            <p class="mt-1 text-sm text-slate-600">
              <span v-if="factureCourante.numero_facture">N° {{ factureCourante.numero_facture }}</span>
              <span v-else>Brouillon</span>
              <span class="ml-2 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">{{ statutLabel(factureCourante.statut) }}</span>
            </p>
          </div>
          <div class="text-sm text-slate-600">
            <div v-if="factureCourante.numero_facture">
              Total : <strong>{{ formatMontant(factureCourante.montant_total) }} FCFA</strong>
              <span v-if="factureCourante.montant_restant > 0" class="ml-2">Reste : {{ formatMontant(factureCourante.montant_restant) }} FCFA</span>
            </div>
            <div v-else>Total : <strong>{{ formatMontant(factureCourante.montant_total) }} FCFA</strong></div>
          </div>
        </div>

        <p
          v-if="factureCourante.montant_paye > 0 || factureCourante.tiers_payant_montant > 0"
          class="mt-4 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-600"
        >
          Payé patient : {{ formatMontant(factureCourante.montant_paye) }} —
          Tiers payant ({{ factureCourante.tiers_payant_organisme || '—' }}) :
          {{ formatMontant(factureCourante.tiers_payant_montant) }}
        </p>

        <div class="mt-6 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Acte</th>
                <th class="px-3 py-3 font-medium">Libellé</th>
                <th class="px-3 py-3 font-medium">Qté</th>
                <th class="px-3 py-3 font-medium">P.U.</th>
                <th class="px-3 py-3 font-medium">Montant</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="l in factureCourante.lignes" :key="l.id" class="hover:bg-slate-50">
                <td class="px-3 py-3 text-slate-700">{{ l.code_acte }}</td>
                <td class="px-3 py-3 text-slate-700">{{ l.libelle }}</td>
                <td class="px-3 py-3 text-slate-700">{{ l.quantite }}</td>
                <td class="px-3 py-3 text-slate-700">{{ formatMontant(l.prix_unitaire) }}</td>
                <td class="px-3 py-3 text-slate-700">{{ formatMontant(l.montant_ligne) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="auth.canFacturation" class="mt-6 flex flex-wrap gap-3 rounded-2xl bg-slate-50 p-4">
          <button
            v-if="factureCourante.statut === 'brouillon'"
            class="rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700"
            @click="valider(factureCourante)"
          >
            Valider la facture
          </button>
          <button
            v-if="['validee', 'partiellement_payee', 'payee'].includes(factureCourante.statut)"
            class="rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            @click="telechargerPdf(factureCourante)"
          >
            PDF signé
          </button>
          <template v-if="['validee', 'partiellement_payee'].includes(factureCourante.statut)">
            <div class="min-w-[180px] space-y-1">
              <label class="text-sm font-medium text-slate-700">Montant patient</label>
              <input
                v-model.number="paiement.montant"
                type="number"
                min="0"
                :placeholder="String(factureCourante.montant_restant)"
                class="w-full rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500"
              />
            </div>
            <div class="min-w-[180px] space-y-1">
              <label class="text-sm font-medium text-slate-700">Tiers payant</label>
              <select v-model="paiement.tiersOrganisme" class="w-full rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500">
                <option value="">— Aucun —</option>
                <option v-for="org in organismes" :key="org.id" :value="org.assurance">{{ org.assurance }} ({{ org.coverage }}%)</option>
              </select>
            </div>
            <div class="min-w-[180px] space-y-1">
              <label class="text-sm font-medium text-slate-700">Montant tiers</label>
              <input v-model.number="paiement.tiersMontant" type="number" min="0" class="w-full rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <div class="min-w-[180px] space-y-1">
              <label class="text-sm font-medium text-slate-700">Mode de paiement</label>
              <select v-model="paiement.mode" class="w-full rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500">
                <option value="especes">Espèces</option>
                <option value="mobile_money">Mobile money</option>
                <option value="virement">Virement</option>
                <option value="carte">Carte bancaire</option>
              </select>
            </div>
            <div class="min-w-[180px] space-y-1">
              <label class="text-sm font-medium text-slate-700">Référence</label>
              <input v-model="paiement.reference" placeholder="N° reçu" class="w-full rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <button class="self-end rounded-2xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700" @click="payer(factureCourante)">
              Enregistrer paiement
            </button>
          </template>
        </div>

        <div v-if="auth.canFacturation && journal.length > 0" class="mt-6">
          <h3 class="text-base font-semibold text-slate-900">Journal comptable</h3>
          <div class="mt-4 overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200 text-sm">
              <thead>
                <tr class="text-left text-slate-600">
                  <th class="px-3 py-3 font-medium">Date</th>
                  <th class="px-3 py-3 font-medium">Type</th>
                  <th class="px-3 py-3 font-medium">Libellé</th>
                  <th class="px-3 py-3 font-medium">Montant</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="e in journal" :key="e.id" class="hover:bg-slate-50">
                  <td class="px-3 py-3 text-slate-700">{{ formatDate(e.created_at) }}</td>
                  <td class="px-3 py-3 text-slate-700">{{ e.type_ecriture }}</td>
                  <td class="px-3 py-3 text-slate-700">{{ e.libelle }}</td>
                  <td class="px-3 py-3 text-slate-700">{{ formatMontant(e.montant) }} FCFA</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Tarifs actes (référentiel)</h2>
        <div class="mt-4 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Code</th>
                <th class="px-3 py-3 font-medium">Libellé</th>
                <th class="px-3 py-3 font-medium">Catégorie</th>
                <th class="px-3 py-3 font-medium">Prix unitaire</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="t in tarifs" :key="t.code" class="hover:bg-slate-50">
                <td class="px-3 py-3 text-slate-700">{{ t.code }}</td>
                <td class="px-3 py-3 text-slate-700">{{ t.libelle }}</td>
                <td class="px-3 py-3 text-slate-700">{{ t.categorie }}</td>
                <td class="px-3 py-3 text-slate-700">{{ formatMontant(t.prix_unitaire) }} FCFA</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import api, { downloadPdf, getErrorMessage, unwrapList } from '../api/client.js'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const aFacturer = ref([])
const tarifs = ref([])
const organismes = ref([])
const factureCourante = ref(null)
const journal = ref([])
const error = ref('')
const message = ref('')
const paiement = reactive({
  mode: 'especes',
  reference: '',
  montant: null,
  tiersOrganisme: '',
  tiersMontant: null,
})

const statutLabels = {
  brouillon: 'Brouillon',
  validee: 'Validée',
  partiellement_payee: 'Partiellement payée',
  payee: 'Payée',
  annulee: 'Annulée',
}

function statutLabel(s) {
  return statutLabels[s] || s
}

function formatMontant(v) {
  if (v == null || v === '') return '—'
  const n = Number(v)
  return Number.isNaN(n) ? v : n.toLocaleString('fr-FR')
}

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('fr-FR')
  } catch {
    return iso
  }
}

async function loadJournal(factureId) {
  journal.value = []
  if (!auth.canFacturation || !factureId) return
  try {
    const { data } = await api.get(`/facturation/factures/${factureId}/journal/`)
    journal.value = unwrapList(data)
  } catch {
    journal.value = []
  }
}

async function loadAll() {
  error.value = ''
  try {
    const [tarifsRes, orgsRes] = await Promise.all([
      api.get('/facturation/tarifs/'),
      auth.canFacturation ? api.get('/assurance/organismes/?actif=true') : Promise.resolve({ data: [] }),
    ])
    tarifs.value = unwrapList(tarifsRes.data)
    organismes.value = unwrapList(orgsRes.data)

    if (auth.canFacturation) {
      const listRes = await api.get('/facturation/hospitalisations-a-facturer/')
      aFacturer.value = unwrapList(listRes.data)
    }
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function generer(hospitalisationId) {
  error.value = ''
  message.value = ''
  try {
    const { data } = await api.post(`/hospitalisations/${hospitalisationId}/facture/generer/`)
    factureCourante.value = data
    await loadJournal(data.id)
    message.value = 'Facture générée à partir des actes (séjour, labo, pharmacie).'
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function ouvrirFacture(factureId) {
  error.value = ''
  try {
    const { data } = await api.get(`/facturation/factures/${factureId}/`)
    factureCourante.value = data
    await loadJournal(factureId)
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function valider(facture) {
  error.value = ''
  try {
    const { data } = await api.post(`/facturation/factures/${facture.id}/valider/`, {
      version: facture.version,
    })
    factureCourante.value = data
    await loadJournal(data.id)
    message.value = `Facture ${data.numero_facture} validée (immuable).`
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function telechargerPdf(facture) {
  error.value = ''
  try {
    const name = facture.numero_facture ? `${facture.numero_facture}.pdf` : `facture-${facture.id}.pdf`
    await downloadPdf(`/facturation/factures/${facture.id}/pdf/`, name)
    message.value = 'PDF signé téléchargé.'
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function payer(facture) {
  error.value = ''
  try {
    const body = {
      version: facture.version,
      mode_paiement: paiement.mode,
      reference_paiement: paiement.reference,
    }
    if (paiement.montant != null && paiement.montant !== '') {
      body.montant = paiement.montant
    }
    if (paiement.tiersMontant != null && paiement.tiersMontant > 0) {
      body.tiers_payant_organisme = paiement.tiersOrganisme
      body.tiers_payant_montant = paiement.tiersMontant
    }
    const { data } = await api.post(`/facturation/factures/${facture.id}/paiement/`, body)
    factureCourante.value = data
    await loadJournal(data.id)
    message.value =
      data.statut === 'payee'
        ? 'Facture soldée.'
        : 'Paiement partiel enregistré (journal comptable mis à jour).'
    paiement.reference = ''
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

onMounted(loadAll)
</script>
