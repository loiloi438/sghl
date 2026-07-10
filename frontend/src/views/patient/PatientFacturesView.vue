<template>
  <div class="space-y-6">
    <PatientPageHeader title="Mes factures" subtitle="Factures validées, paiement en ligne et historique" :loading="loading" @refresh="load" />

    <div v-if="message" class="rounded-3xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
    <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
    <div v-if="loading" class="rounded-3xl border border-slate-200 bg-white px-6 py-5 text-sm text-slate-600 shadow-sm">Chargement…</div>
    <div v-else-if="items.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-6 py-8 text-center text-sm text-slate-600">Aucune facture disponible.</div>

    <div v-else class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
      <table class="min-w-full divide-y divide-slate-200 text-sm">
        <thead class="bg-slate-50 text-slate-500">
          <tr>
            <th class="px-4 py-3 text-left font-semibold">N° facture</th>
            <th class="px-4 py-3 text-left font-semibold">Statut</th>
            <th class="px-4 py-3 text-left font-semibold">Total</th>
            <th class="px-4 py-3 text-left font-semibold">Reste à payer</th>
            <th class="px-4 py-3 text-left font-semibold">Dates</th>
            <th class="px-4 py-3 text-left font-semibold">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr v-for="f in items" :key="f.id" class="hover:bg-slate-50">
            <td class="px-4 py-4 font-mono text-xs text-slate-600">{{ f.numero_facture || '—' }}</td>
            <td class="px-4 py-4">
              <span :class="statutClass(f.statut)">{{ factureStatutLabel(f.statut) }}</span>
            </td>
            <td class="px-4 py-4 text-slate-700">{{ formatMontant(f.montant_total) }} FCFA</td>
            <td class="px-4 py-4 font-semibold text-slate-900">{{ formatMontant(f.montant_restant) }} FCFA</td>
            <td class="px-4 py-4 text-slate-600">
              <div v-if="f.validee_le">Validée : {{ formatPatientDate(f.validee_le) }}</div>
              <div v-if="f.payee_le">Payée : {{ formatPatientDate(f.payee_le) }}</div>
            </td>
            <td class="px-4 py-4">
              <div class="flex flex-wrap gap-2">
                <button
                  v-if="f.payable_en_ligne"
                  type="button"
                  class="rounded-2xl bg-emerald-600 px-3 py-2 text-sm font-semibold text-white hover:bg-emerald-700"
                  @click="openPayment(f)"
                >
                  Payer en ligne
                </button>
                <button
                  type="button"
                  class="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
                  :disabled="downloadingId === f.id"
                  @click="downloadPdf(f)"
                >
                  PDF
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <PatientPaymentModal v-model:open="paymentOpen" :facture="selectedFacture" @success="onPaymentSuccess" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api, { downloadPdf as fetchPdf, getErrorMessage, unwrapList } from '../../api/client.js'
import { factureStatutLabel, formatMontant, formatPatientDate } from '../../composables/usePatientPortal.js'
import PatientPageHeader from '../../components/patient/PatientPageHeader.vue'
import PatientPaymentModal from '../../components/patient/PatientPaymentModal.vue'

const route = useRoute()
const items = ref([])
const loading = ref(true)
const error = ref('')
const message = ref('')
const downloadingId = ref(null)
const paymentOpen = ref(false)
const selectedFacture = ref(null)

function statutClass(statut) {
  const base = 'inline-flex rounded-full px-3 py-1 text-xs font-semibold'
  if (statut === 'payee') return `${base} bg-emerald-100 text-emerald-700`
  if (statut === 'partiellement_payee') return `${base} bg-amber-100 text-amber-700`
  return `${base} bg-slate-100 text-slate-700`
}

function openPayment(facture) {
  selectedFacture.value = facture
  paymentOpen.value = true
}

async function onPaymentSuccess() {
  message.value = 'Paiement enregistré avec succès.'
  paymentOpen.value = false
  selectedFacture.value = null
  await load()
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/patient/factures/')
    items.value = unwrapList(data)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function downloadPdf(f) {
  downloadingId.value = f.id
  message.value = ''
  error.value = ''
  try {
    const name = f.numero_facture ? `${f.numero_facture}.pdf` : `facture-${f.id}.pdf`
    await fetchPdf(`/facturation/factures/${f.id}/pdf/`, name)
    message.value = 'Facture téléchargée.'
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    downloadingId.value = null
  }
}

onMounted(async () => {
  await load()
  if (route.query.payment === 'success') {
    message.value = 'Merci — votre paiement a été traité.'
  }
})
</script>
