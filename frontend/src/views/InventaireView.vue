<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto max-w-7xl space-y-6">
      <header class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Inventaire</h1>
            <p class="mt-1 text-sm text-slate-600">Gestion des stocks consommables et équipements hospitaliers</p>
          </div>
          <div class="flex gap-2">
            <button class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-100" type="button" @click="loadAll">Actualiser</button>
            <button class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800" type="button" @click="showCreateForm = !showCreateForm">+ Nouveau stock</button>
          </div>
        </div>
      </header>

      <div v-if="message" class="rounded-3xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
      <div v-if="error" class="rounded-3xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</div>

      <form v-if="showCreateForm" class="grid gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-2" @submit.prevent="createItem">
        <h2 class="md:col-span-2 text-lg font-semibold text-slate-900">Ajouter un article</h2>
        <input v-model="itemForm.code" required placeholder="Code article" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-sky-500" />
        <input v-model="itemForm.nom" required placeholder="Nom" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-sky-500" />
        <select v-model="itemForm.categorie" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-sky-500">
          <option value="consumable">Consommable</option>
          <option value="equipment">Équipement</option>
          <option value="medication">Médicament</option>
        </select>
        <input v-model.number="itemForm.quantite" type="number" min="0" placeholder="Quantité initiale" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-sky-500" />
        <input v-model.number="itemForm.seuil_alerte" type="number" min="0" placeholder="Seuil d'alerte" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-sky-500" />
        <input v-model="itemForm.unite" placeholder="Unité (pcs, carton…)" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-sky-500" />
        <input v-model.number="itemForm.valeur_unitaire" type="number" min="0" step="0.01" placeholder="Valeur unitaire" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none focus:border-sky-500" />
        <div class="md:col-span-2">
          <button type="submit" class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800" :disabled="saving">Créer l'article</button>
        </div>
      </form>

      <section class="grid gap-4 md:grid-cols-3">
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Articles en stock</span>
          <strong class="mt-4 block text-3xl font-semibold text-slate-900">{{ stats.total_items }}</strong>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Niveaux critiques</span>
          <strong class="mt-4 block text-3xl font-semibold text-rose-600">{{ stats.critical_levels }}</strong>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Valeur totale</span>
          <strong class="mt-4 block text-3xl font-semibold text-slate-900">{{ formatValue(stats.total_value) }}</strong>
        </article>
      </section>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="grid gap-4 lg:grid-cols-[1.2fr_0.9fr_0.9fr]">
          <input v-model="search" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100" type="search" placeholder="Rechercher un article…" @input="debouncedLoad" />
          <select v-model="categoryFilter" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100" @change="loadArticles">
            <option value="">Toutes les catégories</option>
            <option value="consumable">Consommables</option>
            <option value="equipment">Équipements</option>
            <option value="medication">Médicaments</option>
          </select>
          <select v-model="stockFilter" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100">
            <option value="">Tous les niveaux</option>
            <option value="critical">Critique</option>
            <option value="low">Faible</option>
            <option value="normal">Normal</option>
            <option value="high">Élevé</option>
          </select>
        </div>

        <div v-if="loading" class="mt-6 rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">Chargement…</div>
        <div v-else-if="filteredItems.length === 0" class="mt-6 rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">Aucun article trouvé.</div>

        <div v-else class="mt-6 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-slate-500">
              <tr>
                <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Article</th>
                <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Catégorie</th>
                <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Quantité</th>
                <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Seuil alerte</th>
                <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Statut</th>
                <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Valeur</th>
                <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 bg-white">
              <tr v-for="item in filteredItems" :key="item.id" class="hover:bg-slate-50">
                <td class="px-4 py-4 text-slate-700"><strong>{{ item.name }}</strong><br><span class="text-xs text-slate-400">{{ item.code }}</span></td>
                <td class="px-4 py-4"><span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.15em] text-slate-600">{{ categoryLabel(item.category) }}</span></td>
                <td class="px-4 py-4 text-slate-700">{{ item.quantity }} {{ item.unit }}</td>
                <td class="px-4 py-4 text-slate-700">{{ item.minLevel }} {{ item.unit }}</td>
                <td class="px-4 py-4"><span :class="stockStatusClass(item.stockLevel)">{{ stockStatusLabel(item.stockLevel) }}</span></td>
                <td class="px-4 py-4 text-slate-700">{{ formatValue(item.value) }}</td>
                <td class="px-4 py-4 space-x-2">
                  <button class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-3 py-2 text-sm font-semibold text-white transition hover:bg-slate-800" @click="editItem(item)">Ajuster</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <div v-if="adjustModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4" @click.self="closeAdjustModal">
        <form class="w-full max-w-md space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-xl" @submit.prevent="submitAdjust">
          <h2 class="text-lg font-semibold text-slate-900">Ajuster le stock</h2>
          <p class="text-sm text-slate-600">{{ adjustModal.item?.name }} — quantité actuelle : <strong>{{ adjustModal.item?.quantity }}</strong></p>
          <input v-model.number="adjustModal.delta" required type="number" placeholder="Delta (+/-)" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-sky-500" />
          <p class="text-xs text-slate-500">Ex. +10 pour réapprovisionner, -2 pour consommation.</p>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" class="rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50" @click="closeAdjustModal">Annuler</button>
            <button type="submit" class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800" :disabled="saving">Appliquer</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api, { getErrorMessage, unwrapList } from '../api/client.js'

const items = ref([])
const stats = ref({ total_items: 0, critical_levels: 0, total_value: '0' })
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const message = ref('')
const search = ref('')
const categoryFilter = ref('')
const stockFilter = ref('')
const showCreateForm = ref(false)
const adjustModal = ref({ open: false, item: null, delta: 0 })
const itemForm = ref({
  code: '',
  nom: '',
  categorie: 'consumable',
  quantite: 0,
  seuil_alerte: 10,
  unite: 'unité',
  valeur_unitaire: 0,
})

let debounceTimer = null

const filteredItems = computed(() => {
  if (!stockFilter.value) return items.value
  return items.value.filter((item) => item.stockLevel === stockFilter.value)
})

function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadArticles, 300)
}

function formatValue(value) {
  const num = Number(value || 0)
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XAF', maximumFractionDigits: 0 }).format(num)
}

const categoryLabel = (category) => ({
  consumable: 'Consommable',
  equipment: 'Équipement',
  medication: 'Médicament',
}[category] || category)

const stockStatusLabel = (level) => ({
  critical: 'Critique',
  low: 'Faible',
  normal: 'Normal',
  high: 'Élevé',
}[level] || level)

const stockStatusClass = (level) => {
  const map = {
    critical: 'inline-flex rounded-full bg-rose-100 px-2.5 py-1 text-xs font-semibold text-rose-700',
    low: 'inline-flex rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-700',
    normal: 'inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700',
    high: 'inline-flex rounded-full bg-sky-100 px-2.5 py-1 text-xs font-semibold text-sky-700',
  }
  return map[level] || map.normal
}

async function loadStats() {
  const { data } = await api.get('/inventaire/stats/')
  stats.value = data
}

async function loadArticles() {
  const params = new URLSearchParams()
  if (search.value.trim()) params.set('search', search.value.trim())
  if (categoryFilter.value) params.set('categorie', categoryFilter.value)
  const qs = params.toString()
  const { data } = await api.get(`/inventaire/articles/${qs ? `?${qs}` : ''}`)
  items.value = unwrapList(data)
}

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([loadStats(), loadArticles()])
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function createItem() {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    await api.post('/inventaire/articles/', itemForm.value)
    message.value = 'Article créé.'
    itemForm.value = { code: '', nom: '', categorie: 'consumable', quantite: 0, seuil_alerte: 10, unite: 'unité', valeur_unitaire: 0 }
    showCreateForm.value = false
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

function openAdjustModal(item) {
  adjustModal.value = { open: true, item, delta: 0 }
}

function closeAdjustModal() {
  adjustModal.value = { open: false, item: null, delta: 0 }
}

async function submitAdjust() {
  const { item, delta } = adjustModal.value
  if (!item || !delta) return
  saving.value = true
  error.value = ''
  try {
    await api.post(`/inventaire/articles/${item.id}/ajuster/`, { version: item.version, delta })
    message.value = 'Stock ajusté.'
    closeAdjustModal()
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

function editItem(item) {
  openAdjustModal(item)
}

onMounted(loadAll)
</script>
