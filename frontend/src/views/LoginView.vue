<template>
  <div class="min-h-screen bg-slate-50">
    <div class="mx-auto grid min-h-screen max-w-7xl grid-cols-1 gap-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
      <aside class="rounded-[2rem] bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 p-6 text-white shadow-[0_24px_80px_rgba(15,23,42,0.15)] lg:p-10">
        <div class="flex h-full flex-col justify-between gap-8">
          <div class="space-y-6">
            <div class="inline-flex items-center gap-3 rounded-3xl bg-white/10 px-4 py-3 text-sm font-semibold text-slate-100 shadow-sm shadow-slate-950/10">
              <span class="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-teal-400 text-slate-950">+</span>
              <div>
                <div class="text-base font-semibold">SGHL</div>
                <div class="text-xs uppercase tracking-[0.2em] text-slate-300">Centre hospitalier</div>
              </div>
            </div>

            <div class="space-y-4">
              <p class="text-xs uppercase tracking-[0.24em] text-cyan-300">Qualité des soins</p>
              <h1 class="max-w-xl text-4xl font-semibold leading-tight tracking-tight text-white sm:text-5xl">Votre parcours de soins, simplifié</h1>
              <p class="max-w-lg text-sm leading-7 text-slate-200">Une plateforme médicale claire et sécurisée — rendez-vous, prescriptions, résultats et suivi patient en un seul endroit.</p>
            </div>

            <ul class="space-y-3 text-sm text-slate-200">
              <li class="flex items-start gap-3">
                <span class="mt-1 inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400"></span>
                Suivi hospitalier en temps réel
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-1 inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400"></span>
                Documents médicaux téléchargeables
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-1 inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400"></span>
                Prise de rendez-vous en ligne
              </li>
            </ul>
          </div>

          <div class="overflow-hidden rounded-[1.75rem] border border-white/10 bg-white/10">
            <img
              src="/images/login-hero.jpg"
              alt="Professionnel de santé en environnement hospitalier moderne"
              class="block h-full w-full object-cover"
              loading="eager"
            />
          </div>
        </div>
      </aside>

      <main class="flex items-center justify-center px-4 py-8 sm:px-6 lg:px-8">
        <div
          class="w-full max-w-md rounded-[2rem] bg-white p-8 shadow-[0_20px_60px_rgba(15,23,42,0.08)] lg:p-10"
          :class="{ 'login-patient-panel': mode === 'register' }"
        >
          <div class="flex items-center justify-between gap-4">
            <div>
              <p v-if="mode === 'register'" class="login-patient-tag">🌿 Human-Care · Espace patient</p>
              <h2 class="text-2xl font-semibold text-slate-900">{{ panelTitle }}</h2>
              <p class="mt-2 text-sm text-slate-600">{{ panelSubtitle }}</p>
            </div>
            <ThemeToggle />
          </div>

          <div class="mt-6 rounded-3xl bg-slate-50 p-4 text-sm text-slate-700">
            <span class="inline-flex items-center justify-center rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600">Sécurité</span>
            <p class="mt-3 leading-6 text-slate-600">Vos données sont protégées — connexion chiffrée et conforme RGPD.</p>
          </div>

          <div v-if="successMessage" class="mt-5 rounded-3xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ successMessage }}</div>
          <div v-if="localError" class="mt-5 rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ localError }}</div>
          <div v-if="auth.error && mode === 'login'" class="mt-5 rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ auth.error }}</div>
          <div v-if="auth.error && mode === 'mfa'" class="mt-5 rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ auth.error }}</div>

          <form v-if="mode === 'login'" @submit.prevent="submitLogin" class="mt-7 space-y-5">
            <label class="block space-y-2 text-sm text-slate-700">
              <span>Identifiant</span>
              <input
                id="username"
                v-model="username"
                autocomplete="username"
                placeholder="Votre identifiant"
                required
                class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
              />
            </label>

            <label class="block space-y-2 text-sm text-slate-700">
              <span>Mot de passe</span>
              <input
                id="password"
                v-model="password"
                type="password"
                autocomplete="current-password"
                placeholder="••••••••••••"
                required
                class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
              />
            </label>

            <button
              class="w-full rounded-3xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              type="submit"
              :disabled="auth.loading"
            >
              {{ auth.loading ? 'Connexion en cours…' : 'Se connecter' }}
            </button>

            <div class="grid gap-3 text-left text-sm">
              <button type="button" class="text-slate-700 underline decoration-slate-200 transition hover:text-slate-900" @click="switchMode('register')">Nouveau patient ? Créez votre compte</button>
              <button type="button" class="text-slate-700 underline decoration-slate-200 transition hover:text-slate-900" @click="switchMode('forgot')">Mot de passe oublié</button>
            </div>
          </form>

          <form v-else-if="mode === 'mfa'" @submit.prevent="mfaUseTotp ? submitTotpLogin() : submitMfa()" class="mt-7 space-y-6 rounded-[2rem] border border-sky-200 bg-sky-50/80 p-6 shadow-[0_20px_60px_rgba(56,189,248,0.16)]">
            <div class="space-y-3 rounded-3xl border border-sky-300 bg-sky-100 px-4 py-4 text-sm text-slate-900">
              <div class="text-sm font-semibold uppercase tracking-[0.2em] text-sky-700">Étape 2 : Vérification MFA</div>
              <p v-if="!mfaUseTotp" class="text-base font-semibold text-slate-900">Un code a été envoyé à votre adresse e-mail.</p>
              <p v-else class="text-base font-semibold text-slate-900">Saisissez le code de Google Authenticator.</p>
              <p v-if="!mfaUseTotp" class="text-sm text-slate-700">Saisissez le code de 6 chiffres reçu pour terminer la connexion. Le code expire dans 5 minutes.</p>
              <p v-else class="text-sm text-slate-700">Ouvrez votre application d’authentification et entrez le code à 6 chiffres affiché.</p>
            </div>

            <label class="block space-y-2 text-sm text-slate-700">
              <span class="font-semibold">{{ mfaUseTotp ? 'Code Authenticator' : 'Code de sécurité' }}</span>
              <input
                v-if="mfaUseTotp"
                id="totp-code"
                v-model="totpCode"
                inputmode="numeric"
                maxlength="6"
                required
                class="w-full rounded-3xl border border-slate-300 bg-white px-4 py-4 text-lg text-slate-900 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-200"
              />
              <input
                v-else
                id="mfa-code"
                v-model="mfaCode"
                inputmode="numeric"
                maxlength="6"
                required
                class="w-full rounded-3xl border border-slate-300 bg-white px-4 py-4 text-lg text-slate-900 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-200"
              />
            </label>
            <button
              class="w-full rounded-3xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              type="submit"
              :disabled="auth.loading"
            >
              {{ auth.loading ? 'Vérification…' : 'Vérifier le code' }}
            </button>
            <div class="grid gap-3 text-left text-sm">
              <button type="button" class="text-slate-700 underline decoration-slate-200 transition hover:text-slate-900" @click="switchMode('login')">← Retour à la connexion</button>
              <button
                v-if="!mfaUseTotp"
                type="button"
                class="text-sky-700 font-semibold underline decoration-sky-200 transition hover:text-sky-900"
                @click="resendMfaCode"
              >
                Renvoyer le code
              </button>
              <button
                type="button"
                class="text-sky-700 font-semibold underline decoration-sky-200 transition hover:text-sky-900"
                @click="toggleMfaMethod"
              >
                {{ mfaUseTotp ? 'Utiliser le code reçu par e-mail' : 'Utiliser Google Authenticator' }}
              </button>
            </div>
          </form>

          <form v-else-if="mode === 'register'" @submit.prevent="submitRegister" class="mt-7 space-y-5">
            <div class="grid gap-4 sm:grid-cols-2">
              <label class="block space-y-2 text-sm text-slate-700">
                <span>Nom</span>
                <input id="reg-nom" v-model="registerForm.nom" autocomplete="family-name" required class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
              </label>
              <label class="block space-y-2 text-sm text-slate-700">
                <span>Prénom</span>
                <input id="reg-prenom" v-model="registerForm.prenom" autocomplete="given-name" required class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
              </label>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <label class="block space-y-2 text-sm text-slate-700">
                <span>Date de naissance</span>
                <input id="reg-dob" v-model="registerForm.date_naissance" type="date" required class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
              </label>
              <label class="block space-y-2 text-sm text-slate-700">
                <span>Sexe</span>
                <select id="reg-sexe" v-model="registerForm.sexe" required class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200">
                  <option value="M">Masculin</option>
                  <option value="F">Féminin</option>
                  <option value="A">Autre</option>
                </select>
              </label>
            </div>

            <label class="block space-y-2 text-sm text-slate-700">
              <span>E-mail</span>
              <input id="reg-email" v-model="registerForm.email" type="email" autocomplete="email" placeholder="vous@exemple.com" required class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
            </label>

            <label class="block space-y-2 text-sm text-slate-700">
              <span>Téléphone</span>
              <input id="reg-phone" v-model="registerForm.telephone" type="tel" autocomplete="tel" placeholder="+242 06 000 00 00" class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
            </label>
            <p class="text-sm text-slate-500">Un e-mail est requis pour valider votre compte patient.</p>

            <label class="block space-y-2 text-sm text-slate-700">
              <span>Mot de passe</span>
              <input id="reg-password" v-model="registerForm.password" type="password" autocomplete="new-password" required class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
            </label>

            <label class="block space-y-2 text-sm text-slate-700">
              <span>Confirmer le mot de passe</span>
              <input id="reg-password2" v-model="registerForm.password_confirm" type="password" autocomplete="new-password" required class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
            </label>

            <label class="flex items-start gap-3 text-sm text-slate-700">
              <input v-model="registerForm.consentement_rgpd" type="checkbox" required class="mt-1 h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-400" />
              <span>
                J'accepte le traitement de mes données de santé conformément à la
                <a href="#" @click.prevent class="text-slate-900 underline">politique de confidentialité</a> (RGPD).
              </span>
            </label>

            <button class="hc-btn-rdv a11y-touch w-full disabled:cursor-not-allowed disabled:opacity-60" type="submit" :disabled="formLoading">
              {{ formLoading ? 'Création…' : 'Créer mon compte patient' }}
            </button>

            <button type="button" class="text-sm text-slate-600 transition hover:text-slate-900" @click="switchMode('login')">← Retour à la connexion</button>
          </form>

          <form v-else-if="mode === 'forgot'" @submit.prevent="submitForgot" class="mt-7 space-y-5">
            <p class="text-sm text-slate-600">Saisissez votre identifiant ou e-mail. Un lien de réinitialisation sera envoyé par e-mail ou SMS si un compte existe.</p>
            <label class="block space-y-2 text-sm text-slate-700">
              <span>Identifiant ou e-mail</span>
              <input id="forgot-id" v-model="forgotIdentifiant" autocomplete="username" placeholder="Identifiant ou e-mail" required class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
            </label>
            <button class="w-full rounded-3xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60" type="submit" :disabled="formLoading">
              {{ formLoading ? 'Envoi…' : 'Envoyer le lien' }}
            </button>
            <button type="button" class="text-sm text-slate-600 transition hover:text-slate-900" @click="switchMode('login')">← Retour à la connexion</button>
          </form>

          <form v-else-if="mode === 'reset'" @submit.prevent="submitReset" class="mt-7 space-y-5">
            <p class="text-sm text-slate-600">Choisissez un nouveau mot de passe pour votre compte.</p>
            <label class="block space-y-2 text-sm text-slate-700">
              <span>Nouveau mot de passe</span>
              <input id="reset-password" v-model="resetForm.new_password" type="password" autocomplete="new-password" required class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
            </label>
            <label class="block space-y-2 text-sm text-slate-700">
              <span>Confirmer le mot de passe</span>
              <input id="reset-password2" v-model="resetForm.new_password_confirm" type="password" autocomplete="new-password" required class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200" />
            </label>
            <button class="w-full rounded-3xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60" type="submit" :disabled="formLoading">
              {{ formLoading ? 'Mise à jour…' : 'Réinitialiser le mot de passe' }}
            </button>
          </form>

          <p v-if="mode === 'login'" class="mt-6 rounded-3xl bg-slate-50 px-4 py-4 text-sm leading-6 text-slate-600">
            <strong>Personnel hospitalier :</strong> votre compte est créé par l'administration. Pas d'auto-inscription pour les médecins, infirmiers ou autres rôles staff.
          </p>

          <p class="mt-6 text-center text-sm text-slate-500">
            Besoin d'aide ?
            <RouterLink to="/contact" class="font-semibold text-slate-900 underline">Contact & localisation</RouterLink>
            ·
            <a :href="`mailto:${supportEmail}`" class="font-semibold text-slate-900 underline">Support</a>
          </p>

          <p class="mt-6 text-center text-xs uppercase tracking-[0.2em] text-slate-400">SGHL — Patient & staff</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api, { getErrorMessage } from '../api/client.js'
import ThemeToggle from '../components/ThemeToggle.vue'
import { setPortalTheme } from '../composables/useTheme.js'
import { useAuthStore } from '../stores/auth.js'
const router = useRouter()
const route = useRoute()

const mode = ref('login')
const formLoading = ref(false)
const localError = ref('')
const successMessage = ref('')
const supportEmail = 'support@sghl.local'

const username = ref('')
const password = ref('')
const totpCode = ref('')
const mfaCode = ref('')
const mfaUseTotp = ref(false)
const forgotIdentifiant = ref('')

const registerForm = reactive({
  nom: '',
  prenom: '',
  date_naissance: '',
  sexe: 'M',
  email: '',
  telephone: '',
  password: '',
  password_confirm: '',
  consentement_rgpd: false,
})

const resetForm = reactive({
  uid: '',
  token: '',
  new_password: '',
  new_password_confirm: '',
})


const panelTitle = computed(() => {
  if (mode.value === 'register') return 'Créer un compte patient'
  if (mode.value === 'forgot') return 'Mot de passe oublié'
  if (mode.value === 'reset') return 'Nouveau mot de passe'
  if (mode.value === 'mfa') return 'Vérification MFA'
  return 'Connexion'
})

const panelSubtitle = computed(() => {
  if (mode.value === 'register') {
    return 'Inscription réservée aux patients — validation e-mail/SMS'
  }
  if (mode.value === 'forgot') return 'Récupération d\'accès sécurisée'
  if (mode.value === 'reset') return 'Définissez un nouveau mot de passe'
  if (mode.value === 'mfa') {
    return mfaUseTotp.value
      ? 'Entrez le code affiché dans Google Authenticator.'
      : 'Entrez le code reçu par e-mail pour terminer la connexion.'
  }
  return 'Espace patient ou personnel hospitalier'
})

function switchMode(next) {
  mode.value = next
  if (next === 'register') {
    setPortalTheme('patient')
  }
  localError.value = ''
  successMessage.value = ''
  auth.error = null
  mfaCode.value = ''
  totpCode.value = ''
  mfaUseTotp.value = false
}

function toggleMfaMethod() {
  mfaUseTotp.value = !mfaUseTotp.value
  mfaCode.value = ''
  totpCode.value = ''
  auth.error = null
  localError.value = ''
}

function parseResetQuery() {
  const raw = route.query.reset
  if (!raw || typeof raw !== 'string') return
  const dot = raw.indexOf('.')
  if (dot <= 0) return
  resetForm.uid = raw.slice(0, dot)
  resetForm.token = raw.slice(dot + 1)
  mode.value = 'reset'
}

onMounted(parseResetQuery)

async function submitLogin() {
  const res = await auth.login(username.value, password.value)
  if (res === 'mfa_required') {
    mode.value = 'mfa'
    successMessage.value = 'Code MFA envoyé. Vérifiez votre e-mail et saisissez le code reçu.'
    return
  }
  if (res) {
    const defaultRoute = { name: auth.homeRoute }
    router.push(route.query.redirect || defaultRoute)
  }
}

async function submitTotpLogin() {
  localError.value = ''
  successMessage.value = ''
  const res = await auth.login(username.value, password.value, totpCode.value.trim())
  if (res === true) {
    const defaultRoute = { name: auth.homeRoute }
    router.push(route.query.redirect || defaultRoute)
  }
}

async function submitMfa() {
  localError.value = ''
  successMessage.value = ''
  formLoading.value = true
  try {
    const ok = await auth.loginMfa(mfaCode.value.trim())
    if (ok) {
      const defaultRoute = { name: auth.homeRoute }
      router.push(route.query.redirect || defaultRoute)
    }
  } catch (e) {
    localError.value = getErrorMessage(e)
  } finally {
    formLoading.value = false
  }
}

async function resendMfaCode() {
  localError.value = ''
  successMessage.value = ''
  formLoading.value = true
  try {
    const res = await auth.login(username.value, password.value)
    if (res === 'mfa_required') {
      successMessage.value = 'Un nouveau code a été envoyé par e-mail.'
    } else {
      localError.value = 'Impossible de renvoyer le code. Veuillez réessayer.'
    }
  } catch (e) {
    localError.value = getErrorMessage(e)
  } finally {
    formLoading.value = false
  }
}

async function submitRegister() {
  localError.value = ''
  successMessage.value = ''
  formLoading.value = true
    try {
      const { data } = await api.post('/auth/register/patient/', {
        ...registerForm,
        email: registerForm.email.trim(),
        telephone: registerForm.telephone.trim(),
      })
      successMessage.value = data.detail || 'Compte créé.'
      // redirect to validation page with username prefilled
      router.push({ name: 'validate-account', query: { username: data.username } })
  } catch (e) {
    localError.value = getErrorMessage(e)
  } finally {
    formLoading.value = false
  }
}

async function submitForgot() {
  localError.value = ''
  successMessage.value = ''
  formLoading.value = true
  try {
    const { data } = await api.post('/auth/password/forgot/', {
      identifiant: forgotIdentifiant.value.trim(),
    })
    successMessage.value = data.detail
    forgotIdentifiant.value = ''
  } catch (e) {
    localError.value = getErrorMessage(e)
  } finally {
    formLoading.value = false
  }
}

async function submitReset() {
  localError.value = ''
  successMessage.value = ''
  formLoading.value = true
  try {
    const { data } = await api.post('/auth/password/reset/', {
      uid: resetForm.uid,
      token: resetForm.token,
      new_password: resetForm.new_password,
      new_password_confirm: resetForm.new_password_confirm,
    })
    successMessage.value = data.detail
    resetForm.new_password = ''
    resetForm.new_password_confirm = ''
    switchMode('login')
    router.replace({ name: 'login' })
  } catch (e) {
    localError.value = getErrorMessage(e)
  } finally {
    formLoading.value = false
  }
}
</script>
