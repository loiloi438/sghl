<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto max-w-3xl space-y-6">
      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Mon compte</h1>
        <p class="mt-1 text-sm text-slate-600">Profil personnel et sécurité de connexion</p>
      </div>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Informations</h2>
        <dl class="mt-5 grid gap-4 sm:grid-cols-2">
          <div class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3">
            <dt class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Nom</dt>
            <dd class="mt-1 text-sm font-medium text-slate-900">{{ auth.fullName }}</dd>
          </div>
          <div class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3">
            <dt class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Identifiant</dt>
            <dd class="mt-1 text-sm font-medium text-slate-900">{{ auth.user?.username }}</dd>
          </div>
          <div class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3">
            <dt class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">E-mail</dt>
            <dd class="mt-1 text-sm font-medium text-slate-900">{{ auth.user?.email || '—' }}</dd>
          </div>
          <div class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3">
            <dt class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Rôle</dt>
            <dd class="mt-1 text-sm font-medium capitalize text-slate-900">{{ roleLabel }}</dd>
          </div>
        </dl>
      </section>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Authentification MFA (TOTP)</h2>
            <p class="mt-1 text-sm text-slate-600">Google Authenticator ou application compatible</p>
          </div>
          <span
            class="rounded-full px-3 py-1 text-xs font-semibold"
            :class="auth.mfaEnabled ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
          >
            {{ auth.mfaEnabled ? 'Activé' : 'Non configuré' }}
          </span>
        </div>
        <div class="mt-5">
          <MfaTotpSetup />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import MfaTotpSetup from '../components/MfaTotpSetup.vue'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()

const ROLE_LABELS = {
  admin: 'Administrateur',
  medecin: 'Médecin',
  infirmier: 'Infirmier',
  biologiste: 'Biologiste',
  pharmacien: 'Pharmacien',
  comptable: 'Comptable',
}

const roleLabel = computed(() => ROLE_LABELS[auth.user?.role] || auth.user?.role || '—')
</script>
