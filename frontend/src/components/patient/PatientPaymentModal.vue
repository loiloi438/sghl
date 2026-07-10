<template>
  <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4" @click.self="close">
    <div class="w-full max-w-lg space-y-5 rounded-3xl border border-slate-200 bg-white p-6 shadow-xl">
      <div>
        <h2 class="text-lg font-semibold text-slate-900">Payer en ligne</h2>
        <p v-if="facture" class="mt-1 text-sm text-slate-600">
          Facture {{ facture.numero_facture || '—' }} —
          <strong>{{ formatMontant(facture.montant_restant) }} FCFA</strong> restants
        </p>
      </div>

      <div v-if="error" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
      <div v-if="message" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>

      <template v-if="step === 'choose'">
        <label class="grid gap-2 text-sm text-slate-700">
          <span>Mode de paiement</span>
          <select v-model="provider" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400">
            <option value="stripe">Carte bancaire (Stripe)</option>
            <option value="mtn">MTN Mobile Money</option>
            <option value="airtel">Airtel Money</option>
          </select>
        </label>
        <div class="flex justify-end gap-2">
          <button type="button" class="rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50" @click="close">Annuler</button>
          <button type="button" class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60" :disabled="processing" @click="initiate">
            {{ processing ? 'Initialisation…' : 'Continuer' }}
          </button>
        </div>
      </template>

      <template v-else-if="step === 'stripe' && payment">
        <p class="text-sm text-slate-600">Saisissez les informations de votre carte pour finaliser le paiement.</p>
        <div ref="cardMount" class="rounded-2xl border border-slate-200 bg-slate-50 p-4"></div>
        <div class="flex justify-end gap-2">
          <button type="button" class="rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50" @click="close">Fermer</button>
          <button type="button" class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60" :disabled="processing" @click="confirmStripe">
            {{ processing ? 'Paiement…' : 'Payer' }}
          </button>
        </div>
      </template>

      <template v-else-if="step === 'pending' && payment">
        <p class="text-sm leading-6 text-slate-600">
          Paiement Mobile Money initié (réf. <span class="font-mono">{{ payment.reference }}</span>).
          Confirmez la transaction sur votre téléphone, puis cliquez sur « Vérifier le paiement ».
        </p>
        <a
          v-if="payment.redirect_url"
          :href="payment.redirect_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex rounded-2xl bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-sky-700"
        >
          Ouvrir la page de paiement
        </a>
        <div class="flex justify-end gap-2">
          <button type="button" class="rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50" @click="close">Fermer</button>
          <button type="button" class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60" :disabled="processing" @click="pollStatus">
            {{ processing ? 'Vérification…' : 'Vérifier le paiement' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import api, { getErrorMessage } from '../../api/client.js'
import { formatMontant } from '../../composables/usePatientPortal.js'

const props = defineProps({
  open: { type: Boolean, default: false },
  facture: { type: Object, default: null },
})

const emit = defineEmits(['update:open', 'success'])

const provider = ref('stripe')
const step = ref('choose')
const payment = ref(null)
const processing = ref(false)
const error = ref('')
const message = ref('')
const cardMount = ref(null)

let stripe = null
let cardElement = null

const stripeKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || ''

function close() {
  emit('update:open', false)
  reset()
}

function reset() {
  step.value = 'choose'
  payment.value = null
  processing.value = false
  error.value = ''
  message.value = ''
  destroyCardElement()
}

function destroyCardElement() {
  if (cardElement) {
    cardElement.unmount()
    cardElement = null
  }
}

async function initiate() {
  if (!props.facture) return
  processing.value = true
  error.value = ''
  message.value = ''
  try {
    const { data } = await api.post(`/patient/factures/${props.facture.id}/initier-paiement/`, {
      provider: provider.value,
      version: props.facture.version,
    })
    payment.value = data

    if (data.facture_settled || data.status === 'success') {
      message.value = 'Paiement enregistré — facture soldée.'
      emit('success', data)
      return
    }

    if (data.client_secret && stripeKey) {
      step.value = 'stripe'
      await nextTick()
      await mountStripe(data.client_secret)
      return
    }

    if (data.client_secret && !stripeKey) {
      error.value = 'Clé Stripe publique manquante (VITE_STRIPE_PUBLISHABLE_KEY).'
      return
    }

    step.value = 'pending'
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    processing.value = false
  }
}

async function mountStripe() {
  destroyCardElement()
  const { loadStripe } = await import('@stripe/stripe-js')
  stripe = await loadStripe(stripeKey)
  if (!stripe || !cardMount.value) {
    error.value = 'Impossible de charger Stripe.'
    return
  }
  const elements = stripe.elements()
  cardElement = elements.create('card', { hidePostalCode: true })
  cardElement.mount(cardMount.value)
}

async function confirmStripe() {
  if (!stripe || !payment.value?.client_secret) return
  processing.value = true
  error.value = ''
  try {
    const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(payment.value.client_secret, {
      payment_method: { card: cardElement },
    })
    if (stripeError) {
      error.value = stripeError.message || 'Paiement refusé.'
      return
    }
    if (paymentIntent?.status === 'succeeded') {
      await pollStatus()
    }
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    processing.value = false
  }
}

async function pollStatus() {
  if (!payment.value?.reference) return
  processing.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/payments/${payment.value.reference}/status/`)

    if (data.status === 'success' && data.facture_settled) {
      message.value = 'Paiement confirmé — facture mise à jour.'
      emit('success', data)
      return
    }
    if (data.status === 'success' && data.settlement_error) {
      error.value = data.settlement_error
      return
    }
    if (data.status === 'failed') {
      error.value = 'Paiement échoué.'
      return
    }
    message.value = 'Paiement encore en attente — réessayez dans quelques instants.'
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    processing.value = false
  }
}

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) reset()
  },
)

onBeforeUnmount(destroyCardElement)
</script>
