<template>

  <div class="hc-page">

    <PatientPageHeader
      title="Messagerie"
      subtitle="Échangez en toute confiance avec votre médecin ou le secrétariat"
      module="message"
      :loading="loading"
      @refresh="load"
    />



    <div v-if="error" class="hc-alert hc-alert--error">{{ error }}</div>

    <div v-if="sentOk" class="hc-alert hc-alert--success">Message envoyé — nous vous répondrons rapidement 💙</div>



    <section class="hc-card hc-card-padded">

      <h2 class="text-sm font-bold uppercase tracking-widest text-teal-800">Nouveau message</h2>

      <form class="mt-4 space-y-4" @submit.prevent="send">

        <label class="block space-y-1 text-sm text-slate-700">

          <span class="font-semibold">Sujet</span>

          <input

            v-model="form.sujet"

            required

            class="a11y-touch w-full rounded-2xl border border-emerald-100 bg-emerald-50/30 px-4 py-3 outline-none focus:border-teal-400 focus:ring-2 focus:ring-teal-100"

            placeholder="Ex. Question sur mon rendez-vous"

          />

        </label>

        <label class="block space-y-1 text-sm text-slate-700">

          <span class="font-semibold">Message</span>

          <textarea

            v-model="form.corps"

            required

            rows="4"

            class="a11y-touch w-full rounded-2xl border border-emerald-100 bg-emerald-50/30 px-4 py-3 outline-none focus:border-teal-400 focus:ring-2 focus:ring-teal-100"

            placeholder="Décrivez votre demande…"

          />

        </label>

        <button type="submit" class="hc-btn-rdv a11y-touch" :disabled="sending">

          {{ sending ? 'Envoi…' : '✉️ Envoyer au secrétariat' }}

        </button>

      </form>

    </section>



    <section class="hc-card hc-card-padded">

      <h2 class="font-bold text-teal-900" style="font-family: Poppins, sans-serif">Mes échanges</h2>



      <PatientEmptyState

        v-if="messages.length === 0"

        icon="💬"

        title="Aucun message pour l’instant"

        text="Vos conversations avec l’équipe médicale s’afficheront ici."

        class="mt-4"

      />



      <div v-else class="hc-chat mt-4">

        <div

          v-for="m in messages"

          :key="m.id"

          class="hc-chat-bubble"

          :class="m.sens === 'recu' ? 'hc-chat-bubble--in' : 'hc-chat-bubble--out'"

        >

          <strong class="block text-sm">{{ m.sujet }}</strong>

          <p class="mt-1">{{ m.corps }}</p>

          <p class="mt-2 text-[11px] opacity-70">

            {{ m.expediteur_nom }} · {{ m.sens === 'recu' ? 'Reçu' : 'Envoyé' }}

            · {{ formatPatientDate(m.created_at) }}

          </p>

        </div>

      </div>

    </section>

  </div>

</template>



<script setup>

import { onMounted, reactive, ref } from 'vue'

import api, { getErrorMessage } from '../../api/client.js'

import { formatPatientDate } from '../../composables/usePatientPortal.js'

import PatientEmptyState from '../../components/patient/PatientEmptyState.vue'

import PatientPageHeader from '../../components/patient/PatientPageHeader.vue'



const messages = ref([])
const loading = ref(true)
const error = ref('')

const sentOk = ref(false)

const sending = ref(false)

const form = reactive({ sujet: '', corps: '' })



async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/patient/messages/')
    messages.value = data
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}



async function send() {

  sending.value = true

  error.value = ''

  sentOk.value = false

  try {

    await api.post('/patient/messages/', form)

    form.sujet = ''

    form.corps = ''

    sentOk.value = true

    await load()

  } catch (e) {

    error.value = getErrorMessage(e)

  } finally {

    sending.value = false

  }

}



onMounted(load)

</script>


