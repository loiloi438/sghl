<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <div class="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-slate-900">{{ title }}</h1>
          <p class="mt-1 text-sm text-slate-600">{{ subtitle }}</p>
        </div>
        <button class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" type="button" @click="loadPersonnel">Actualiser</button>
      </div>

      <div v-if="error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</div>

      <div class="grid gap-4 md:grid-cols-3">
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Effectif</span>
          <div class="mt-2 text-3xl font-semibold text-slate-900">{{ personnel.length }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">MFA actif</span>
          <div class="mt-2 text-3xl font-semibold text-slate-900">{{ mfaEnabledCount }}</div>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Recherche</span>
          <div class="mt-2 text-lg font-semibold text-slate-900">{{ search || 'Aucune' }}</div>
        </article>
      </div>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <input v-model="search" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500 md:max-w-md" type="search" placeholder="Rechercher par nom ou e-mail…" @input="debouncedLoad" />
        </div>

        <div v-if="loading" class="text-sm text-slate-500">Chargement…</div>
        <div v-else-if="personnel.length === 0" class="text-sm text-slate-500">Aucun membre trouvé.</div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Personnel</th>
                <th class="px-3 py-3 font-medium">E-mail</th>
                <th class="px-3 py-3 font-medium">Rôle</th>
                <th class="px-3 py-3 font-medium">MFA</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="person in personnel" :key="person.id" class="hover:bg-slate-50">
                <td class="px-3 py-3">
                  <div class="flex items-center gap-3">
                    <img v-if="person.photo_url" :src="person.photo_url" alt="Photo {{ person.full_name }}" class="h-10 w-10 rounded-full object-cover" />
                    <div v-else class="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 font-semibold text-white">
                      {{ person.full_name.split(' ').map((part) => part[0]).join('').slice(0, 2) }}
                    </div>
                    <div>
                      <div class="font-semibold text-slate-900">{{ person.full_name }}</div>
                      <div class="mt-1 text-xs text-slate-500">{{ person.username }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-3 py-3 text-slate-700">{{ person.email || '—' }}</td>
                <td class="px-3 py-3"><span class="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">{{ person.role_label }}</span></td>
                <td class="px-3 py-3 text-slate-700">{{ person.mfa_enabled ? 'Activé' : 'Non' }}</td>
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
import api, { getErrorMessage, unwrapList } from '../api/client.js'

const route = useRoute()
const personnel = ref([])
const loading = ref(true)
const error = ref('')
const search = ref('')
let timer

const title = computed(() => route.meta.title || 'Personnel')
const subtitle = computed(() => route.meta.subtitle || 'Annuaire du personnel médical')
const endpoint = computed(() => (route.name === 'personnel-infirmiers' ? '/personnel/infirmiers/' : '/personnel/medecins/'))
const mfaEnabledCount = computed(() => personnel.value.filter((item) => item.mfa_enabled).length)

function debouncedLoad() {
  clearTimeout(timer)
  timer = setTimeout(loadPersonnel, 300)
}

async function loadPersonnel() {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (search.value) params.set('search', search.value)
    const { data } = await api.get(`${endpoint.value}${params.toString() ? `?${params.toString()}` : ''}`)
    personnel.value = unwrapList(data)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadPersonnel)
</script>

