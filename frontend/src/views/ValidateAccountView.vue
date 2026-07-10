<template>
  <div class="min-h-screen bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
    <div class="mx-auto w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
      <div class="space-y-4 text-center">
        <h2 class="text-2xl font-semibold tracking-tight text-slate-900">Validation du compte</h2>
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
            class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
          />
        </div>

        <div class="space-y-2">
          <label for="val-code" class="block text-sm font-medium text-slate-700">Code de validation</label>
          <input
            id="val-code"
            v-model="code"
            maxlength="10"
            required
            class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="inline-flex w-full items-center justify-center rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {{ loading ? 'Validation…' : 'Valider' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-slate-600">
        Vous n'avez pas reçu le code ?
        <button
          type="button"
          class="ml-1 font-semibold text-slate-900 hover:text-slate-700 disabled:cursor-not-allowed disabled:text-slate-400"
          @click="resend"
          :disabled="resendLoading"
        >
          Renvoyer
        </button>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { getErrorMessage } from '../api/client.js'
import Toast from '../components/Toast.vue'

const route = useRoute()
const router = useRouter()

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
    setTimeout(() => router.push({ name: 'login' }), 800)
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
