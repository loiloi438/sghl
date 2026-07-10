<template>
  <transition name="toast-fade">
    <div v-if="visible" class="toast" :class="type">
      {{ text }}
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue'
const visible = ref(false)
const text = ref('')
const type = ref('')
let timer = null

function show(message, _type = 'info', duration = 4000) {
  if (timer) clearTimeout(timer)
  text.value = message
  type.value = _type
  visible.value = true
  timer = setTimeout(() => (visible.value = false), duration)
}

function hide() {
  if (timer) clearTimeout(timer)
  visible.value = false
}

defineExpose({ show, hide })
</script>

<style scoped>
.toast {
  position: fixed;
  right: 1rem;
  top: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  color: #fff;
  box-shadow: 0 6px 18px rgba(0,0,0,0.12);
  z-index: 1200;
}
.toast.info { background: #2563eb; }
.toast.success { background: #16a34a; }
.toast.error { background: #dc2626; }
.toast-fade-enter-active, .toast-fade-leave-active { transition: opacity 0.25s; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; }
</style>
