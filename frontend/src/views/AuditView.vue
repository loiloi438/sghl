<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto max-w-7xl space-y-6">
      <header class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Journal d'audit</h1>
            <p class="mt-1 text-sm text-slate-600">Traçabilité des actions sur le système (admin)</p>
          </div>
          <button class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50" type="button" @click="load">Actualiser</button>
        </div>
      </header>

      <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 shadow-sm">{{ error }}</div>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="grid gap-4 lg:grid-cols-2">
          <label for="filter-model" class="space-y-2">
            <span class="text-sm font-semibold text-slate-700">Modèle</span>
            <input
              id="filter-model"
              v-model="filterModel"
              type="search"
              placeholder="ex. Prescription"
              @input="debouncedLoad"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
            />
          </label>
          <label for="filter-action" class="space-y-2">
            <span class="text-sm font-semibold text-slate-700">Action</span>
            <select
              id="filter-action"
              v-model="filterAction"
              @change="load"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
            >
              <option value="">Toutes</option>
              <option value="CREATE">Création</option>
              <option value="UPDATE">Modification</option>
              <option value="DELETE">Suppression</option>
            </select>
          </label>
        </div>
      </section>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div v-if="loading" class="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">Chargement…</div>
        <div v-else-if="logs.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">Aucune entrée d'audit.</div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-slate-500">
              <tr>
                <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Date</th>
                <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Utilisateur</th>
                <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Action</th>
                <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Modèle</th>
                <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">Objet</th>
                <th class="px-4 py-3 text-left font-semibold uppercase tracking-[0.1em]">IP</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 bg-white">
              <tr v-for="log in logs" :key="log.id" class="hover:bg-slate-50">
                <td class="px-4 py-4 text-slate-700">{{ formatDate(log.timestamp) }}</td>
                <td class="px-4 py-4 text-slate-700">{{ log.utilisateur || '—' }}</td>
                <td class="px-4 py-4"><span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-700">{{ log.action }}</span></td>
                <td class="px-4 py-4 text-slate-700">{{ log.model_name }}</td>
                <td class="px-4 py-4 text-slate-700 font-mono text-xs">{{ log.object_id }}</td>
                <td class="px-4 py-4 text-slate-700">{{ log.ip_address || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { getErrorMessage, unwrapList } from '../api/client.js'

const logs = ref([])
const loading = ref(true)
const error = ref('')
const filterModel = ref('')
const filterAction = ref('')
let timer

function debouncedLoad() {
  clearTimeout(timer)
  timer = setTimeout(load, 300)
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('fr-FR')
  } catch {
    return iso
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (filterModel.value) params.set('model_name', filterModel.value)
    if (filterAction.value) params.set('action', filterAction.value)
    const qs = params.toString()
    const { data } = await api.get(`/audit/logs/${qs ? `?${qs}` : ''}`)
    logs.value = unwrapList(data)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

