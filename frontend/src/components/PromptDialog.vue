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
      <form class="w-full max-w-md space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-xl" @submit.prevent="submit">
        <h2 :id="titleId" class="text-lg font-semibold text-slate-900">{{ title }}</h2>
        <p v-if="message" class="text-sm leading-6 text-slate-600">{{ message }}</p>
        <label class="grid gap-2 text-sm text-slate-700">
          <span v-if="inputLabel">{{ inputLabel }}</span>
          <input
            ref="inputRef"
            v-model="localValue"
            :type="inputType"
            :placeholder="placeholder"
            class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
          />
        </label>
        <div class="flex justify-end gap-2 pt-2">
          <button
            type="button"
            class="rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
            :disabled="loading"
            @click="$emit('cancel')"
          >
            Annuler
          </button>
          <button
            type="submit"
            class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-60"
            :disabled="loading"
          >
            {{ loading ? 'Enregistrement…' : confirmLabel }}
          </button>
        </div>
      </form>
    </div>
  </Teleport>
</template>

<script setup>
import { nextTick, ref, useId, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: 'Saisie' },
  message: { type: String, default: '' },
  modelValue: { type: String, default: '' },
  inputLabel: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  inputType: { type: String, default: 'text' },
  confirmLabel: { type: String, default: 'Valider' },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['confirm', 'cancel', 'update:modelValue'])

const titleId = useId()
const inputRef = ref(null)
const localValue = ref(props.modelValue)

watch(
  () => props.open,
  async (isOpen) => {
    if (!isOpen) return
    localValue.value = props.modelValue
    await nextTick()
    inputRef.value?.focus()
  },
)

watch(localValue, (value) => emit('update:modelValue', value))

function submit() {
  emit('confirm', localValue.value)
}
</script>
