<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { getErrorMessage } from '../api/client.js'
import { useAuthStore } from '../stores/auth.js'
import Toast from '../components/Toast.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const username = ref(route.query.username || '')
const code = ref('')
const loading = ref(false)
const resendLoading = ref(false)
const message = ref('')
const error = ref('')
const toastRef = ref(null)

async function submitValidate() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.post('/auth/validate/', {
      username: username.value,
      code: code.value.trim(),
    })
    message.value = data.detail
    toastRef.value?.show(data.detail || 'Compte activé', 'success')
    const ok = await auth.applyTokens(data.access_token, data.refresh_token)
    if (ok) {
      router.push({ name: 'patient-home' })
    } else {
      error.value = auth.error || 'Connexion automatique impossible.'
    }
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function resend() {
  resendLoading.value = true
  error.value = ''
  try {
    const { data } = await api.post('/auth/validate/resend/', { username: username.value })
    message.value = data.detail
    toastRef.value?.show(data.detail || 'Nouveau code envoyé', 'success')
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    resendLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-teal-50/50 px-4 py-10 sm:px-6 lg:px-8">
    <div class="mx-auto w-full max-w-md rounded-3xl border border-teal-100 bg-white p-8 shadow-sm">
      <div class="space-y-4 text-center">
        <p class="text-sm font-medium text-teal-700">🌿 Human-Care</p>
        <h2 class="text-2xl font-semibold tracking-tight text-teal-950">Validation du compte</h2>
        <p class="text-sm leading-6 text-slate-600">Un code de validation vous a été envoyé par e-mail. Saisissez-le ci‑dessous pour activer votre compte.</p>
      </div>

      <div class="mt-6 space-y-4">
        <div v-if="message" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
        <div v-if="error" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
        <Toast ref="toastRef" />
      </div>

      <form @submit.prevent="submitValidate" class="mt-6 space-y-5">
        <div class="space-y-2">
          <label for="val-username" class="block text-sm font-medium text-slate-700">Identifiant</label>
          <input
            id="val-username"
            v-model="username"
            required
            class="a11y-touch w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
          />
        </div>

        <div class="space-y-2">
          <label for="val-code" class="block text-sm font-medium text-slate-700">Code de validation</label>
          <input
            id="val-code"
            v-model="code"
            maxlength="10"
            required
            class="a11y-touch w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="a11y-touch inline-flex w-full items-center justify-center rounded-2xl bg-teal-700 px-4 py-3 text-sm font-semibold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {{ loading ? 'Validation…' : 'Valider et accéder à mon espace' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-slate-600">
        Vous n'avez pas reçu le code ?
        <button
          type="button"
          class="ml-1 font-semibold text-teal-900 hover:text-teal-700 disabled:cursor-not-allowed disabled:text-slate-400"
          @click="resend"
          :disabled="resendLoading"
        >
          Renvoyer
        </button>
      </p>
    </div>
  </div>
</template>
