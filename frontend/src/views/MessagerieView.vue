<template>
  <div class="tech-dashboard space-y-6">
    <div class="glass-card p-6">
      <h1 class="text-2xl font-semibold text-sky-100">Messagerie interne</h1>
      <p class="mt-1 text-sm text-slate-400">Échanges sécurisés entre équipes et patients</p>
    </div>

    <div v-if="error" class="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{{ error }}</div>

    <div class="grid gap-6 lg:grid-cols-2">
      <form class="glass-card space-y-4 p-6" @submit.prevent="send">
        <h2 class="text-lg font-semibold text-white">Nouveau message</h2>
        <label class="block space-y-1 text-sm text-slate-300">
          <span>Destinataire</span>
          <select v-model.number="form.destinataire_id" required class="a11y-touch w-full rounded-xl border border-slate-600 bg-slate-900 px-3 py-2 text-white">
            <option v-for="c in contacts" :key="c.id" :value="c.id">{{ c.full_name }} ({{ c.role_label }})</option>
          </select>
        </label>
        <label class="block space-y-1 text-sm text-slate-300">
          <span>Sujet</span>
          <input v-model="form.sujet" required class="a11y-touch w-full rounded-xl border border-slate-600 bg-slate-900 px-3 py-2 text-white" />
        </label>
        <label class="block space-y-1 text-sm text-slate-300">
          <span>Message</span>
          <textarea v-model="form.corps" required rows="4" class="a11y-touch w-full rounded-xl border border-slate-600 bg-slate-900 px-3 py-2 text-white" />
        </label>
        <button type="submit" class="a11y-touch rounded-xl bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500" :disabled="sending">
          {{ sending ? 'Envoi…' : 'Envoyer' }}
        </button>
      </form>

      <div class="glass-card p-6">
        <h2 class="text-lg font-semibold text-white">Boîte de réception</h2>
        <ul class="mt-4 max-h-[28rem] space-y-3 overflow-y-auto">
          <li
            v-for="m in messages"
            :key="m.id"
            class="rounded-2xl border border-slate-600/50 p-4"
            :class="!m.lu && m.sens === 'recu' ? 'bg-sky-500/10' : 'bg-slate-900/40'"
          >
            <div class="flex items-start justify-between gap-2">
              <strong class="text-sm text-white">{{ m.sujet }}</strong>
              <span class="text-xs text-slate-400">{{ m.sens === 'recu' ? 'Reçu' : 'Envoyé' }}</span>
            </div>
            <p class="mt-2 text-sm text-slate-300">{{ m.corps }}</p>
            <p class="mt-2 text-xs text-slate-500">{{ m.expediteur_nom }} → {{ m.destinataire_nom }}</p>
            <button
              v-if="!m.lu && m.sens === 'recu'"
              type="button"
              class="a11y-touch mt-3 text-xs font-semibold text-sky-300 hover:text-sky-200"
              @click="markRead(m)"
            >
              Marquer comme lu
            </button>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import api, { getErrorMessage } from '../api/client.js'

const messages = ref([])
const contacts = ref([])
const error = ref('')
const sending = ref(false)
const form = reactive({ destinataire_id: null, sujet: '', corps: '' })

async function load() {
  error.value = ''
  try {
    const [msgRes, contactRes] = await Promise.all([
      api.get('/messagerie/'),
      api.get('/messagerie/contacts/'),
    ])
    messages.value = msgRes.data
    contacts.value = contactRes.data
    if (contacts.value.length && !form.destinataire_id) {
      form.destinataire_id = contacts.value[0].id
    }
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function send() {
  sending.value = true
  error.value = ''
  try {
    await api.post('/messagerie/', form)
    form.sujet = ''
    form.corps = ''
    await load()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    sending.value = false
  }
}

async function markRead(m) {
  await api.post(`/messagerie/${m.id}/lu/`)
  m.lu = true
}

onMounted(load)
</script>
