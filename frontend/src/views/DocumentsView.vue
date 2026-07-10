<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <div class="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Documents médicaux</h1>
          <p class="mt-1 text-sm text-slate-600">Archivage, signature et téléchargement des PDF métier</p>
        </div>
        <button class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" type="button" @click="loadDocuments">Actualiser</button>
      </div>

      <div v-if="error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</div>

      <div class="grid gap-4 md:grid-cols-3">
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Documents</span>
          <div class="mt-2 text-3xl font-semibold text-slate-900">{{ documents.length }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Filtre type</span>
          <div class="mt-2 text-lg font-semibold text-slate-900">{{ typeLabel }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Recherche</span>
          <div class="mt-2 text-lg font-semibold text-slate-900">{{ search || 'Aucune' }}</div>
        </article>
      </div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <input v-model="search" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500 md:max-w-md" type="search" placeholder="Rechercher un document…" @input="debouncedLoad" />
          <select v-model="typeFilter" @change="loadDocuments" class="rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500">
            <option value="">Tous les types</option>
            <option value="facture">Facture</option>
            <option value="compte_rendu_labo">Compte-rendu laboratoire</option>
            <option value="ordonnance">Ordonnance</option>
          </select>
        </div>

        <div v-if="loading" class="mt-6 text-sm text-slate-500">Chargement…</div>
        <div v-else-if="documents.length === 0" class="mt-6 text-sm text-slate-500">Aucun document signé trouvé.</div>
        <div v-else class="mt-6 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Type</th>
                <th class="px-3 py-3 font-medium">Référence</th>
                <th class="px-3 py-3 font-medium">Patient</th>
                <th class="px-3 py-3 font-medium">Signataire</th>
                <th class="px-3 py-3 font-medium">Signé le</th>
                <th class="px-3 py-3 font-medium">Vérification</th>
                <th class="px-3 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="document in documents" :key="document.id" class="hover:bg-slate-50">
                <td class="px-3 py-3">
                  <span class="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">{{ document.type_label }}</span>
                </td>
                <td class="px-3 py-3">
                  <div class="font-semibold text-slate-900">{{ document.numero_reference || '—' }}</div>
                  <div class="mt-1 text-xs text-slate-500">Code {{ document.code_verification }}</div>
                </td>
                <td class="px-3 py-3">
                  <div class="font-semibold text-slate-900">{{ document.patient_nom || '—' }}</div>
                  <div class="mt-1 text-xs text-slate-500">{{ document.patient_dossier || '—' }}</div>
                </td>
                <td class="px-3 py-3">
                  <div class="font-semibold text-slate-900">{{ document.signataire_nom }}</div>
                  <div class="mt-1 text-xs text-slate-500">{{ document.signataire_role }}</div>
                </td>
                <td class="px-3 py-3 text-slate-700">{{ formatDate(document.signe_le) }}</td>
                <td class="px-3 py-3">
                  <a :href="document.verification_path" target="_blank" rel="noreferrer" class="text-sm font-semibold text-blue-600 hover:text-blue-700">Ouvrir</a>
                </td>
                <td class="px-3 py-3">
                  <button class="rounded-xl bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-700" type="button" @click="download(document)">PDF</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api, { downloadPdf, getErrorMessage, unwrapList } from '../api/client.js'

const documents = ref([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const route = useRoute()
const typeFilter = ref('')
let searchTimer

const typeLabel = computed(() => {
  if (!typeFilter.value) return 'Tous'
  return {
    facture: 'Facture',
    compte_rendu_labo: 'Compte-rendu labo',
    ordonnance: 'Ordonnance',
  }[typeFilter.value] || typeFilter.value
})

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('fr-FR')
  } catch {
    return iso
  }
}

function debouncedLoad() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadDocuments, 300)
}

async function loadDocuments() {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (search.value) params.set('search', search.value)
    if (typeFilter.value) params.set('type_document', typeFilter.value)
    const { data } = await api.get(`/documents/${params.toString() ? `?${params.toString()}` : ''}`)
    documents.value = unwrapList(data)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

function download(document) {
  const slug = document.numero_reference || document.code_verification || 'document'
  downloadPdf(document.download_path, `${slug}.pdf`)
}

onMounted(() => {
  if (route.query.search) search.value = String(route.query.search)
  loadDocuments()
})
</script>

