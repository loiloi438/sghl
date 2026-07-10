<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[1200] flex items-center justify-center bg-slate-900/40 p-4"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="titleId"
      @click.self="$emit('cancel')"
    >
      <div class="w-full max-w-md space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-xl">
        <h2 :id="titleId" class="text-lg font-semibold text-slate-900">{{ title }}</h2>
        <p class="text-sm leading-6 text-slate-600">{{ message }}</p>
        <div class="flex justify-end gap-2 pt-2">
          <button
            type="button"
            class="rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
            :disabled="loading"
            @click="$emit('cancel')"
          >
            {{ cancelLabel }}
          </button>
          <button
            type="button"
            class="rounded-2xl px-4 py-2.5 text-sm font-semibold text-white transition disabled:opacity-60"
            :class="danger ? 'bg-rose-600 hover:bg-rose-700' : 'bg-slate-900 hover:bg-slate-800'"
            :disabled="loading"
            @click="$emit('confirm')"
          >
            {{ loading ? 'Traitement…' : confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useId } from 'vue'

defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: 'Confirmer' },
  message: { type: String, default: '' },
  confirmLabel: { type: String, default: 'Confirmer' },
  cancelLabel: { type: String, default: 'Annuler' },
  danger: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})

defineEmits(['confirm', 'cancel'])

const titleId = useId()
</script>
