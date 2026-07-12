<template>
  <div class="hc-page">
    <PatientPageHeader
      title="Factures"
      subtitle="Historique des paiements et téléchargement de vos reçus"
      module="invoice"
      :loading="loading"
      @refresh="load"
    />

    <div v-if="message" class="hc-alert hc-alert--success">{{ message }}</div>
    <div v-if="error" class="hc-alert hc-alert--error">{{ error }}</div>
    <div v-if="loading" class="hc-loading">Chargement de vos factures…</div>

    <PatientEmptyState
      v-else-if="items.length === 0"
      icon="🧾"
      title="Aucune facture"
      text="Vos documents de facturation apparaîtront ici lorsqu’ils seront disponibles."
    />

    <div v-else class="hc-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-emerald-50/80 text-teal-800">
            <tr>
              <th class="px-4 py-3 text-left font-bold">N° facture</th>
              <th class="px-4 py-3 text-left font-bold">Statut</th>
              <th class="px-4 py-3 text-left font-bold">Total</th>
              <th class="px-4 py-3 text-left font-bold">Reste</th>
              <th class="px-4 py-3 text-left font-bold">Dates</th>
              <th class="px-4 py-3 text-left font-bold">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-emerald-50">
            <tr v-for="f in items" :key="f.id" class="hover:bg-emerald-50/30">
              <td class="px-4 py-4 font-mono text-xs text-slate-600">{{ f.numero_facture || '—' }}</td>
              <td class="px-4 py-4">
                <span class="hc-badge" :class="`hc-badge--${factureStatutMeta(f.statut).badge}`">
                  {{ factureStatutMeta(f.statut).icon }} {{ factureStatutLabel(f.statut) }}
                </span>
              </td>
              <td class="px-4 py-4 text-slate-700">{{ formatMontant(f.montant_total) }} FCFA</td>
              <td class="px-4 py-4 font-semibold text-slate-900">{{ formatMontant(f.montant_restant) }} FCFA</td>
              <td class="px-4 py-4 text-xs text-slate-600">
                <div v-if="f.validee_le">Validée : {{ formatPatientDate(f.validee_le) }}</div>
                <div v-if="f.payee_le">Payée : {{ formatPatientDate(f.payee_le) }}</div>
              </td>
              <td class="px-4 py-4">
                <div class="flex flex-wrap gap-2">
                  <button
                    v-if="f.payable_en_ligne"
                    type="button"
                    class="hc-btn-rdv !min-h-0 !px-3 !py-2 !text-sm"
                    @click="openPayment(f)"
                  >
                    Payer en ligne
                  </button>
                  <button
                    type="button"
                    class="hc-btn-secondary"
                    :disabled="downloadingId === f.id"
                    @click="downloadFacture(f)"
                  >
                    Facture PDF
                  </button>
                  <button
                    v-if="f.statut === 'payee' || f.statut === 'partiellement_payee'"
                    type="button"
                    class="hc-btn-secondary"
                    :disabled="downloadingRecuId === f.id"
                    @click="downloadRecu(f)"
                  >
                    {{ downloadingRecuId === f.id ? '…' : '📥 Reçu PDF' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <PatientPaymentModal v-model:open="paymentOpen" :facture="selectedFacture" @success="onPaymentSuccess" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api, { downloadPdf as fetchPdf, getErrorMessage, unwrapList } from '../../api/client.js'
import {
  factureStatutLabel,
  factureStatutMeta,
  formatMontant,
  formatPatientDate,
} from '../../composables/usePatientPortal.js'
import PatientEmptyState from '../../components/patient/PatientEmptyState.vue'
import PatientPageHeader from '../../components/patient/PatientPageHeader.vue'
import PatientPaymentModal from '../../components/patient/PatientPaymentModal.vue'

const route = useRoute()
const items = ref([])
const loading = ref(true)
const error = ref('')
const message = ref('')
const downloadingId = ref(null)
const downloadingRecuId = ref(null)
const paymentOpen = ref(false)
const selectedFacture = ref(null)

function openPayment(facture) {
  selectedFacture.value = facture
  paymentOpen.value = true
}

async function onPaymentSuccess() {
  message.value = 'Merci — votre paiement a été enregistré 💙'
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

async function downloadFacture(f) {
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

async function downloadRecu(f) {
  downloadingRecuId.value = f.id
  message.value = ''
  error.value = ''
  try {
    const name = f.numero_facture ? `recu-${f.numero_facture}.pdf` : `recu-${f.id}.pdf`
    await fetchPdf(`/facturation/factures/${f.id}/recu/`, name)
    message.value = 'Reçu téléchargé avec succès.'
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    downloadingRecuId.value = null
  }
}

onMounted(async () => {
  await load()
  if (route.query.payment === 'success') {
    message.value = 'Merci — votre paiement a été traité 💙'
  }
})
</script>
