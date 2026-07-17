<template>
  <div class="tech-dashboard comptes-page">
    <header class="glass-card page-hero">
      <div>
        <p class="kicker">Administration</p>
        <h1>Gestion des comptes</h1>
        <p class="sub">Création et suivi des comptes utilisateurs (RBAC)</p>
      </div>
      <button class="btn-primary" type="button" @click="openCreate()">Créer un compte</button>
    </header>

    <div v-if="error" class="error-box">{{ error }}</div>
    <div v-if="success" class="success-box">{{ success }}</div>

    <section class="glass-card filters">
      <input v-model="search" type="search" placeholder="Rechercher nom, e-mail, identifiant…" @input="debouncedLoad" />
      <select v-model="roleFilter" @change="load">
        <option value="">Tous les rôles</option>
        <option v-for="opt in roleOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
      <button class="btn-ghost" type="button" @click="load">Actualiser</button>
    </section>

    <section v-if="showForm" class="glass-card form-card">
      <h2>{{ form.role === 'medecin' ? 'Ajouter un médecin' : 'Nouveau compte' }}</h2>
      <form class="form-grid" @submit.prevent="submitCreate">
        <label>
          Identifiant
          <input v-model="form.username" required autocomplete="off" />
        </label>
        <label>
          E-mail
          <input v-model="form.email" type="email" autocomplete="off" />
        </label>
        <label>
          Prénom
          <input v-model="form.first_name" required />
        </label>
        <label>
          Nom
          <input v-model="form.last_name" required />
        </label>
        <label>
          Rôle
          <select v-model="form.role" required>
            <option v-for="opt in roleOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </label>
        <label>
          Mot de passe temporaire
          <input v-model="form.password" type="password" required minlength="8" autocomplete="new-password" />
        </label>
        <div class="form-actions">
          <button class="btn-ghost" type="button" @click="showForm = false">Annuler</button>
          <button class="btn-primary" type="submit" :disabled="saving">
            {{ saving ? 'Création…' : 'Enregistrer' }}
          </button>
        </div>
      </form>
    </section>

    <section class="glass-card table-card">
      <div v-if="loading" class="empty">Chargement…</div>
      <div v-else-if="!comptes.length" class="empty">Aucun compte trouvé.</div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Utilisateur</th>
              <th>E-mail</th>
              <th>Rôle</th>
              <th>Statut</th>
              <th>Créé</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="compte in comptes" :key="compte.id">
              <td>
                <strong>{{ compte.full_name }}</strong>
                <span>{{ compte.username }}</span>
              </td>
              <td>{{ compte.email || '—' }}</td>
              <td><span class="role-pill">{{ compte.role_label }}</span></td>
              <td>
                <span :class="['status', compte.is_active ? 'on' : 'off']">
                  {{ compte.is_active ? 'Actif' : 'Inactif' }}
                </span>
              </td>
              <td>{{ formatDate(compte.date_joined) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { getErrorMessage } from '../api/client.js'

const route = useRoute()
const router = useRouter()

const comptes = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')
const search = ref('')
const roleFilter = ref('')
const showForm = ref(false)
let searchTimer = null

const roleOptions = [
  { value: 'admin', label: 'Administrateur' },
  { value: 'medecin', label: 'Médecin' },
  { value: 'infirmier', label: 'Infirmier(ère)' },
  { value: 'biologiste', label: 'Biologiste' },
  { value: 'pharmacien', label: 'Pharmacien' },
  { value: 'comptable', label: 'Comptable' },
  { value: 'secretaire', label: 'Secrétaire' },
  { value: 'patient', label: 'Patient' },
]

const form = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  role: 'medecin',
  password: '',
})

function openCreate(preferredRole = 'medecin') {
  form.username = ''
  form.email = ''
  form.first_name = ''
  form.last_name = ''
  form.role = preferredRole || 'medecin'
  form.password = ''
  showForm.value = true
  success.value = ''
  error.value = ''
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function debouncedLoad() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(load, 300)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/comptes/', {
      params: {
        search: search.value || undefined,
        role: roleFilter.value || undefined,
      },
    })
    comptes.value = data
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function submitCreate() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await api.post('/comptes/', { ...form })
    success.value = `Compte « ${form.username} » créé.`
    showForm.value = false
    await load()
    router.replace({ query: {} })
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

watch(
  () => route.query,
  (query) => {
    if (query.nouveau) {
      openCreate(typeof query.role === 'string' ? query.role : 'medecin')
    }
  },
  { immediate: true },
)

onMounted(load)
</script>

<style scoped>
.comptes-page {
  display: grid;
  gap: 1rem;
}

.page-hero {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 1.2rem 1.35rem;
}

.kicker {
  margin: 0;
  color: #7dd3fc;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.page-hero h1,
.form-card h2 {
  margin: 0.2rem 0;
  color: #f8fafc;
}

.sub {
  margin: 0;
  color: #94a3b8;
  font-size: 0.88rem;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  padding: 0.9rem 1rem;
}

.filters input,
.filters select,
.form-grid input,
.form-grid select {
  min-height: 2.5rem;
  border-radius: 0.8rem;
  border: 1px solid rgba(56, 189, 248, 0.25);
  background: rgba(15, 23, 42, 0.7);
  color: #e2e8f0;
  padding: 0.45rem 0.75rem;
}

.filters input {
  flex: 1;
  min-width: 220px;
}

.btn-primary,
.btn-ghost {
  min-height: 2.5rem;
  border-radius: 0.8rem;
  padding: 0 1rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-primary {
  border: none;
  background: linear-gradient(135deg, #2dd4bf, #38bdf8);
  color: #0b1220;
}

.btn-ghost {
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: transparent;
  color: #e2e8f0;
}

.form-card,
.table-card {
  padding: 1.1rem 1.2rem;
}

.form-grid {
  display: grid;
  gap: 0.75rem;
  margin-top: 0.85rem;
}

@media (min-width: 720px) {
  .form-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.form-grid label {
  display: grid;
  gap: 0.35rem;
  color: #cbd5e1;
  font-size: 0.82rem;
}

.form-actions {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-end;
  gap: 0.55rem;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

th,
td {
  text-align: left;
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  color: #cbd5e1;
}

th {
  color: #94a3b8;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

td strong {
  display: block;
  color: #f8fafc;
}

td span {
  color: #64748b;
  font-size: 0.78rem;
}

.role-pill,
.status {
  display: inline-flex;
  border-radius: 999px;
  padding: 0.2rem 0.55rem;
  font-size: 0.72rem;
  font-weight: 700;
}

.role-pill {
  background: rgba(56, 189, 248, 0.15);
  color: #7dd3fc;
}

.status.on {
  background: rgba(52, 211, 153, 0.15);
  color: #6ee7b7;
}

.status.off {
  background: rgba(248, 113, 113, 0.15);
  color: #fca5a5;
}

.error-box,
.success-box,
.empty {
  border-radius: 0.9rem;
  padding: 0.85rem 1rem;
}

.error-box {
  border: 1px solid rgba(244, 63, 94, 0.4);
  background: rgba(127, 29, 29, 0.35);
  color: #fecdd3;
}

.success-box {
  border: 1px solid rgba(45, 212, 191, 0.35);
  background: rgba(6, 78, 59, 0.35);
  color: #99f6e4;
}

.empty {
  color: #94a3b8;
}
</style>
