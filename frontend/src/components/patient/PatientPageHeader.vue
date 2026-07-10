<template>
  <div class="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:justify-between">
    <div>
      <h1 class="text-2xl font-semibold tracking-tight text-slate-900">{{ title }}</h1>
      <p v-if="subtitle" class="mt-1 text-sm text-slate-600">{{ subtitle }}</p>
    </div>
    <button
      type="button"
      class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
      :disabled="loading"
      @click="$emit('refresh')"
    >
      Actualiser
    </button>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

defineEmits(['refresh'])
</script>
