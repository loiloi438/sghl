<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <header class="border-b border-white/10 bg-slate-900/80 backdrop-blur">
      <div class="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">SGHL — Téléconsultation</p>
          <h1 class="mt-1 text-xl font-semibold tracking-tight text-white">Salle de visioconférence</h1>
        </div>
        <router-link
          :to="homeLink"
          class="inline-flex items-center justify-center rounded-2xl border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-semibold text-slate-100 transition hover:bg-white/10"
        >
          Retour à l'accueil
        </router-link>
      </div>
    </header>

    <main class="mx-auto max-w-6xl space-y-6 px-4 py-6 sm:px-6">
      <div v-if="loading" class="rounded-3xl border border-white/10 bg-slate-900 px-6 py-10 text-center text-sm text-slate-300">
        Chargement de la salle…
      </div>

      <div v-else-if="error" class="rounded-3xl border border-rose-400/30 bg-rose-950/40 px-6 py-8 text-center">
        <h2 class="text-lg font-semibold text-rose-100">Lien indisponible</h2>
        <p class="mt-2 text-sm text-rose-200/90">{{ error }}</p>
      </div>

      <template v-else-if="session">
        <section class="grid gap-4 rounded-3xl border border-white/10 bg-slate-900 p-6 md:grid-cols-[1.2fr_0.8fr]">
          <div class="space-y-3">
            <div class="flex flex-wrap items-center gap-2">
              <span class="rounded-full bg-sky-500/15 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-sky-300">
                {{ statutLabel(session.statut) }}
              </span>
              <span class="text-sm text-slate-400">{{ session.duree_minutes }} min</span>
            </div>
            <h2 class="text-2xl font-semibold text-white">{{ session.motif }}</h2>
            <p class="text-sm text-slate-300">
              <span class="font-medium text-slate-100">Patient :</span> {{ session.patientName }}
            </p>
            <p class="text-sm text-slate-300">
              <span class="font-medium text-slate-100">Médecin :</span> Dr {{ session.doctorName }}
            </p>
            <p class="text-sm text-slate-300">
              <span class="font-medium text-slate-100">Rendez-vous :</span> {{ session.dateTime }}
            </p>
          </div>

          <div class="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Accès à la salle</p>
            <p v-if="session.can_join" class="mt-3 text-sm leading-6 text-emerald-300">
              La salle est ouverte. Autorisez la caméra et le micro pour rejoindre la consultation.
            </p>
            <p v-else class="mt-3 text-sm leading-6 text-amber-200">{{ session.join_message }}</p>
            <p class="mt-4 text-xs text-slate-500">
              Ouverture : {{ formatIso(session.opens_at) }} · Fermeture : {{ formatIso(session.closes_at) }}
            </p>
          </div>
        </section>

        <section v-if="session.can_join && !joined" class="rounded-3xl border border-white/10 bg-slate-900 p-6">
          <h3 class="text-lg font-semibold text-white">Avant de rejoindre</h3>
          <p class="mt-2 text-sm text-slate-300">
            Vérifiez votre identité affichée dans la salle et votre environnement (connexion stable, lieu calme).
          </p>
          <label class="mt-5 grid max-w-md gap-2 text-sm text-slate-200">
            <span>Nom affiché dans la visio</span>
            <input
              v-model="displayName"
              type="text"
              required
              maxlength="80"
              class="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
              placeholder="Votre nom"
            />
          </label>
          <button
            type="button"
            class="mt-5 inline-flex rounded-2xl bg-sky-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="!displayName.trim()"
            @click="joined = true"
          >
            Rejoindre la consultation
          </button>
        </section>

        <section v-if="session.can_join && joined" class="overflow-hidden rounded-3xl border border-white/10 bg-black shadow-2xl">
          <iframe
            :src="jitsiUrl"
            allow="camera; microphone; fullscreen; display-capture; autoplay"
            class="aspect-video w-full min-h-[420px] border-0 bg-black"
            title="Salle de téléconsultation SGHL"
          />
        </section>
      </template>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api, { getErrorMessage } from '../api/client.js'
import { useAuthStore } from '../stores/auth.js'

const route = useRoute()
const auth = useAuthStore()

const loading = ref(true)
const error = ref('')
const session = ref(null)
const joined = ref(false)
const displayName = ref('')

const homeLink = computed(() => {
  if (auth.isAuthenticated) return { name: auth.homeRoute }
  return { name: 'login' }
})

const statutLabel = (statut) => ({
  planifie: 'Planifiée',
  confirme: 'Confirmée',
  annule: 'Annulée',
  termine: 'Terminée',
  absent: 'Absente',
}[statut] || statut)

function formatIso(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' })
  } catch {
    return iso
  }
}

function defaultDisplayName() {
  if (!auth.user) return ''
  if (auth.user.role === 'medecin') {
    const name = auth.fullName || auth.user.username
    return name.startsWith('Dr') ? name : `Dr ${name}`
  }
  return auth.fullName || auth.user.username
}

const jitsiUrl = computed(() => {
  if (!session.value || !displayName.value.trim()) return ''
  const domain = session.value.jitsi_domain
  const room = session.value.room_name
  const name = encodeURIComponent(displayName.value.trim())
  const params = [
    'config.prejoinPageEnabled=false',
    'config.disableDeepLinking=true',
    'interfaceConfig.SHOW_JITSI_WATERMARK=false',
    `userInfo.displayName=${name}`,
  ].join('&')
  return `https://${domain}/${room}#${params}`
})

async function loadSession() {
  loading.value = true
  error.value = ''
  session.value = null
  joined.value = false
  try {
    const { data } = await api.get(`/visio/${route.params.token}/`)
    session.value = data
    displayName.value = defaultDisplayName()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

watch(
  () => route.params.token,
  () => loadSession(),
)

onMounted(loadSession)
</script>
