<template>
  <RouterView />
  <Toast ref="toastRef" />
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { RouterView } from 'vue-router'
import Toast from './components/Toast.vue'
import { registerToastHandler } from './composables/useToast.js'

const toastRef = ref(null)
let unregister = null

onMounted(() => {
  unregister = registerToastHandler((message, type, duration) => {
    toastRef.value?.show(message, type, duration)
  })
})

onUnmounted(() => {
  unregister?.()
})
</script>
