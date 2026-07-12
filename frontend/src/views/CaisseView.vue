<template>
  <div class="tech-dashboard space-y-6">
    <div class="glass-card p-6">
      <h1 class="text-2xl font-semibold text-sky-100">🧬 Caisse & Secrétariat</h1>
      <p class="mt-1 text-sm text-slate-400">Encaissements, statuts de paiement et reçus PDF</p>
    </div>

    <div v-if="message" class="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">{{ message }}</div>
    <div v-if="error" class="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{{ error }}</div>

    <div class="grid gap-4 md:grid-cols-3">
      <article class="glass-card kpi-glow p-5">
        <p class="text-xs uppercase tracking-widest text-sky-300">En attente</p>
        <p class="mt-2 text-3xl font-bold text-white">{{ pendingCount }}</p>
      </article>
      <article class="glass-card kpi-glow p-5">
        <p class="text-xs uppercase tracking-widest text-emerald-300">Payées</p>
        <p class="mt-2 text-3xl font-bold text-white">{{ paidCount }}</p>
      </article>
      <article class="glass-card kpi-glow p-5">
        <p class="text-xs uppercase tracking-widest text-violet-300">Partielles</p>
        <p class="mt-2 text-3xl font-bold text-white">{{ partialCount }}</p>
      </article>
    </div>

    <div class="glass-card overflow-x-auto p-4">
      <table class="min-w-full text-sm text-slate-200">
        <thead>
          <tr class="border-b border-slate-600 text-left text-slate-400">
            <th class="px-3 py-3">N° facture</th>
            <th class="px-3 py-3">Patient</th>
            <th class="px-3 py-3">Montant</th>
            <th class="px-3 py-3">Statut</th>
            <th class="px-3 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in factures" :key="f.id" class="border-b border-slate-700/50 hover:bg-slate-800/40">
            <td class="px-3 py-3">{{ f.numero_facture || '—' }}</td>
            <td class="px-3 py-3">{{ f.patient_nom }}</td>
            <td class="px-3 py-3">{{ formatMontant(f.montant_total) }} FCFA</td>
            <td class="px-3 py-3">
              <span :class="statutClass(f.statut)" class="rounded-full px-2.5 py-1 text-xs font-semibold">{{ statutLabel(f.statut) }}</span>
            </td>
            <td class="px-3 py-3">
              <div class="flex flex-wrap gap-2">
                <button
                  v-if="auth.canFacturation && ['validee', 'partiellement_payee'].includes(f.statut)"
                  class="a11y-touch rounded-xl bg-sky-600 px-3 py-2 text-xs font-semibold text-white hover:bg-sky-500"
                  @click="encaisser(f)"
                >
                  Encaisser
                </button>
                <button
                  v-if="['payee', 'partiellement_payee'].includes(f.statut)"
                  class="a11y-touch rounded-xl border border-slate-500 px-3 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-800"
                  @click="telechargerRecu(f)"
                >
                  Reçu PDF
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api, { getErrorMessage } from '../api/client.js'
import { useAuthStore } from '../stores/auth.js'
import { formatMontant, factureStatutLabel } from '../composables/usePatientPortal.js'

const auth = useAuthStore()
const factures = ref([])
const error = ref('')
const message = ref('')

const pendingCount = computed(() => factures.value.filter((f) => f.statut === 'validee').length)
const paidCount = computed(() => factures.value.filter((f) => f.statut === 'payee').length)
const partialCount = computed(() => factures.value.filter((f) => f.statut === 'partiellement_payee').length)

function statutLabel(s) {
  return factureStatutLabel(s)
}

function statutClass(s) {
  if (s === 'payee') return 'bg-emerald-500/20 text-emerald-200'
  if (s === 'validee') return 'bg-amber-500/20 text-amber-200'
  if (s === 'partiellement_payee') return 'bg-sky-500/20 text-sky-200'
  return 'bg-slate-500/20 text-slate-300'
}

async function load() {
  error.value = ''
  try {
    const { data } = await api.get('/facturation/factures/')
    factures.value = data
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function encaisser(f) {
  if (!auth.canFacturation) return
  try {
    await api.post(`/facturation/factures/${f.id}/paiement/`, {
      montant: f.montant_restant || f.montant_total,
      mode_paiement: 'especes',
      reference_paiement: `CAISSE-${Date.now()}`,
    })
    message.value = 'Paiement enregistré.'
    await load()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function telechargerRecu(f) {
  try {
    const response = await api.get(`/facturation/factures/${f.id}/recu/`, { responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `recu-${f.numero_facture || f.id}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

onMounted(load)
</script>
