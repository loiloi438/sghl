<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto max-w-6xl space-y-6">
      <div class="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Paramètres</h1>
          <p class="mt-1 text-sm text-slate-600">Configuration système, sécurité et profil organisationnel</p>
        </div>
        <button
          class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          type="button"
          @click="saveSettings"
          :disabled="!hasChanges || saving || loading"
        >
          {{ saving ? 'Enregistrement…' : 'Enregistrer les modifications' }}
        </button>
      </div>

      <div v-if="loading" class="rounded-3xl border border-slate-200 bg-white px-4 py-5 text-sm text-slate-600 shadow-sm">Chargement des paramètres…</div>

      <template v-else>
        <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 shadow-sm">{{ error }}</div>
        <div v-if="success" class="rounded-3xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700 shadow-sm">Paramètres mis à jour avec succès.</div>

        <div class="grid gap-6">
          <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">Profil organisationnel</h2>
            <div class="mt-5 grid gap-4">
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Nom de l'établissement</span>
                <input v-model="settings.organizationName" type="text" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
              </label>
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Adresse</span>
                <textarea v-model="settings.address" rows="3" class="min-h-[96px] rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"></textarea>
              </label>
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Téléphone</span>
                <input v-model="settings.phone" type="tel" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
              </label>
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Email support</span>
                <input v-model="settings.email" type="email" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
              </label>
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Numéro FINESS</span>
                <input v-model="settings.finessNumber" type="text" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
              </label>
            </div>
          </section>

          <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">Sécurité</h2>
            <div class="mt-5 grid gap-4">
              <label class="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                <input v-model="settings.mfaRequired" type="checkbox" class="mt-1 h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-400" />
                <span>Authentification multi-facteurs obligatoire</span>
              </label>
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Durée de session (minutes)</span>
                <input v-model.number="settings.sessionTimeout" type="number" min="15" max="1440" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
              </label>
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Nombre maximum de tentatives de connexion</span>
                <input v-model.number="settings.maxLoginAttempts" type="number" min="1" max="20" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
              </label>
              <label class="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                <input v-model="settings.auditLoggingEnabled" type="checkbox" class="mt-1 h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-400" />
                <span>Enregistrement d'audit complet activé</span>
              </label>
              <label class="grid gap-2 text-sm text-slate-700">
                <span>Niveau de chiffrement des données</span>
                <select v-model="settings.encryptionLevel" class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200">
                  <option value="standard">Standard (AES-256)</option>
                  <option value="high">Renforcé (AES-256 + HSM)</option>
                </select>
              </label>
              <label class="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                <input v-model="settings.maintenanceMode" type="checkbox" class="mt-1 h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-400" />
                <span>Mode maintenance</span>
              </label>
              <label v-if="settings.maintenanceMode" class="grid gap-2 text-sm text-slate-700">
                <span>Message de maintenance</span>
                <textarea v-model="settings.maintenanceMessage" rows="2" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400"></textarea>
              </label>
            </div>
          </section>

          <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">Intégrations API</h2>
            <div class="mt-5 grid gap-4">
              <label class="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                <input v-model="settings.hl7Enabled" type="checkbox" class="mt-1 h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-400" />
                <span>Interopérabilité HL7 activée</span>
              </label>
              <label class="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                <input v-model="settings.fhirEnabled" type="checkbox" class="mt-1 h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-400" />
                <span>API FHIR activée</span>
              </label>
              <label class="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                <input v-model="settings.insuranceAPIEnabled" type="checkbox" class="mt-1 h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-400" />
                <span>API assurances activée</span>
              </label>
            </div>
          </section>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api, { getErrorMessage } from '../api/client.js'

const settings = ref(defaultSettings())
const originalSettings = ref({})
const version = ref(1)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref(false)

function defaultSettings() {
  return {
    organizationName: '',
    address: '',
    phone: '',
    email: '',
    finessNumber: '',
    mfaRequired: true,
    sessionTimeout: 60,
    maxLoginAttempts: 5,
    auditLoggingEnabled: true,
    encryptionLevel: 'standard',
    maintenanceMode: false,
    maintenanceMessage: '',
    hl7Enabled: false,
    fhirEnabled: false,
    insuranceAPIEnabled: true,
  }
}

function fromApi(data) {
  return {
    organizationName: data.organization_name || '',
    address: data.address || '',
    phone: data.phone || '',
    email: data.email || '',
    finessNumber: data.finess_number || '',
    mfaRequired: data.mfa_required ?? true,
    sessionTimeout: data.session_timeout_minutes ?? 60,
    maxLoginAttempts: data.max_login_attempts ?? 5,
    auditLoggingEnabled: data.audit_logging_enabled ?? true,
    encryptionLevel: data.encryption_level || 'standard',
    maintenanceMode: data.maintenance_mode ?? false,
    maintenanceMessage: data.maintenance_message || '',
    hl7Enabled: data.hl7_enabled ?? false,
    fhirEnabled: data.fhir_enabled ?? false,
    insuranceAPIEnabled: data.insurance_api_enabled ?? true,
  }
}

function toApiPayload() {
  return {
    version: version.value,
    organization_name: settings.value.organizationName,
    address: settings.value.address,
    phone: settings.value.phone,
    email: settings.value.email,
    finess_number: settings.value.finessNumber,
    mfa_required: settings.value.mfaRequired,
    session_timeout_minutes: settings.value.sessionTimeout,
    max_login_attempts: settings.value.maxLoginAttempts,
    audit_logging_enabled: settings.value.auditLoggingEnabled,
    encryption_level: settings.value.encryptionLevel,
    maintenance_mode: settings.value.maintenanceMode,
    maintenance_message: settings.value.maintenanceMessage,
    hl7_enabled: settings.value.hl7Enabled,
    fhir_enabled: settings.value.fhirEnabled,
    insurance_api_enabled: settings.value.insuranceAPIEnabled,
  }
}

const hasChanges = computed(() => JSON.stringify(settings.value) !== JSON.stringify(originalSettings.value))

async function loadSettings() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/parametres/')
    settings.value = fromApi(data)
    version.value = data.version
    originalSettings.value = JSON.parse(JSON.stringify(settings.value))
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function saveSettings() {
  saving.value = true
  error.value = ''
  success.value = false
  try {
    const { data } = await api.patch('/parametres/', toApiPayload())
    settings.value = fromApi(data)
    version.value = data.version
    originalSettings.value = JSON.parse(JSON.stringify(settings.value))
    success.value = true
    setTimeout(() => { success.value = false }, 3000)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

onMounted(loadSettings)
</script>
