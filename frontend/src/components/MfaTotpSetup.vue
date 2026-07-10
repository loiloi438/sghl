<template>
  <div class="space-y-5">
    <div v-if="auth.mfaEnabled" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-4">
      <div class="flex flex-wrap items-center gap-2">
        <span class="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
        <p class="text-sm font-semibold text-emerald-800">Authentification TOTP activée</p>
      </div>
      <p class="mt-2 text-sm leading-6 text-emerald-900/80">
        Vous pouvez vous connecter avec Google Authenticator (ou une application compatible) ou recevoir un code par e-mail à chaque connexion.
      </p>
    </div>

    <template v-else>
      <p class="text-sm leading-6 text-slate-600">
        Le personnel hospitalier doit activer l’authentification multi-facteurs. Configurez Google Authenticator pour générer des codes à 6 chiffres.
      </p>

      <div v-if="error" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>

      <button
        v-if="!setupData"
        type="button"
        class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
        :disabled="loading"
        @click="startSetup"
      >
        {{ loading ? 'Préparation…' : 'Configurer Google Authenticator' }}
      </button>

      <div v-else class="space-y-5 rounded-2xl border border-sky-200 bg-sky-50/60 p-5">
        <div class="space-y-2">
          <p class="text-sm font-semibold text-slate-900">1. Scannez le QR code</p>
          <p class="text-sm text-slate-600">Ouvrez Google Authenticator, appuyez sur « + », puis scannez ce code.</p>
        </div>

        <div class="flex flex-col items-start gap-4 sm:flex-row sm:items-center">
          <img
            v-if="qrImageUrl"
            :src="qrImageUrl"
            alt="QR code Google Authenticator"
            width="220"
            height="220"
            class="rounded-2xl border border-slate-200 bg-white p-2 shadow-sm"
          />
          <div class="space-y-3 text-sm text-slate-700">
            <p class="font-medium text-slate-900">Saisie manuelle</p>
            <p>Si le scan échoue, entrez cette clé secrète dans l’application :</p>
            <div class="flex flex-wrap items-center gap-2">
              <code class="rounded-xl border border-slate-200 bg-white px-3 py-2 font-mono text-xs tracking-wide text-slate-900">{{ setupData.secret }}</code>
              <button
                type="button"
                class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-100"
                @click="copySecret"
              >
                Copier
              </button>
            </div>
            <p class="text-xs text-slate-500">Compte : {{ auth.user?.username }}</p>
          </div>
        </div>

        <form class="space-y-4" @submit.prevent="confirmEnable">
          <label class="grid gap-2 text-sm text-slate-700">
            <span class="font-semibold text-slate-900">2. Saisissez le code à 6 chiffres</span>
            <input
              v-model="confirmCode"
              inputmode="numeric"
              maxlength="6"
              autocomplete="one-time-code"
              placeholder="000000"
              required
              class="max-w-xs rounded-2xl border border-slate-200 bg-white px-4 py-3 text-lg tracking-[0.3em] text-slate-900 outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-200"
            />
          </label>

          <div class="flex flex-wrap gap-3">
            <button
              type="submit"
              class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="loading || confirmCode.trim().length !== 6"
            >
              {{ loading ? 'Activation…' : 'Activer MFA' }}
            </button>
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              :disabled="loading"
              @click="cancelSetup"
            >
              Annuler
            </button>
          </div>
        </form>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import api, { getErrorMessage } from '../api/client.js'
import { showToast } from '../composables/useToast.js'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()

const loading = ref(false)
const error = ref('')
const setupData = ref(null)
const confirmCode = ref('')

const qrImageUrl = computed(() => {
  if (!setupData.value?.provisioning_uri) return null
  const data = encodeURIComponent(setupData.value.provisioning_uri)
  return `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${data}`
})

async function startSetup() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await api.post('/auth/mfa/setup/')
    setupData.value = data
    confirmCode.value = ''
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

function cancelSetup() {
  setupData.value = null
  confirmCode.value = ''
  error.value = ''
}

async function copySecret() {
  if (!setupData.value?.secret) return
  try {
    await navigator.clipboard.writeText(setupData.value.secret)
    showToast('Clé secrète copiée.', 'success')
  } catch {
    showToast('Impossible de copier automatiquement.', 'error')
  }
}

async function confirmEnable() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await api.post('/auth/mfa/enable/', { code: confirmCode.value.trim() })
    await auth.refreshUser()
    setupData.value = null
    confirmCode.value = ''
    showToast(data.detail || 'MFA activé.', 'success')
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}
</script>
