<template>
  <form class="pub-contact-form" @submit.prevent="submit">
    <h2 class="pub-section-title" style="font-size: 1.35rem">Écrivez-nous</h2>
    <p class="pub-section-sub">Une question ? Laissez votre message — nous vous répondrons rapidement.</p>

    <div v-if="success" class="pub-form-success">{{ success }}</div>
    <div v-if="error" class="pub-form-error">{{ error }}</div>

    <label>
      <span>Nom</span>
      <input v-model.trim="form.nom" type="text" name="nom" required maxlength="120" autocomplete="name" />
    </label>
    <label>
      <span>E-mail</span>
      <input v-model.trim="form.email" type="email" name="email" required maxlength="254" autocomplete="email" />
    </label>
    <label>
      <span>Message</span>
      <textarea v-model.trim="form.message" name="message" required rows="5" maxlength="2000" />
    </label>
    <button class="btn-public-primary" type="submit" :disabled="loading">
      {{ loading ? 'Envoi…' : 'Envoyer le message' }}
    </button>
  </form>
</template>

<script setup>
import { reactive, ref } from 'vue'
import api, { getErrorMessage } from '../../api/client.js'

const form = reactive({
  nom: '',
  email: '',
  message: '',
})
const loading = ref(false)
const error = ref('')
const success = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await api.post('/contact/', {
      nom: form.nom,
      email: form.email,
      message: form.message,
    })
    success.value = 'Merci 💙 Votre message a bien été envoyé. Nous vous répondrons dès que possible.'
    form.nom = ''
    form.email = ''
    form.message = ''
  } catch (e) {
    const status = e?.response?.status
    if (!status || status >= 500) {
      const subject = encodeURIComponent(`Contact SGHL — ${form.nom}`)
      const body = encodeURIComponent(`${form.message}\n\n— ${form.nom} <${form.email}>`)
      window.location.href = `mailto:info@sghl-sante.com?subject=${subject}&body=${body}`
      success.value = 'Ouverture de votre messagerie… Si rien ne s’ouvre, écrivez à info@sghl-sante.com.'
    } else {
      error.value = getErrorMessage(e)
    }
  } finally {
    loading.value = false
  }
}
</script>
