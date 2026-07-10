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
      <form
        class="flex max-h-[90vh] w-full max-w-lg flex-col gap-4 overflow-hidden rounded-3xl border border-slate-200 bg-white p-6 shadow-xl"
        @submit.prevent="submit"
      >
        <div>
          <h2 :id="titleId" class="text-lg font-semibold text-slate-900">Saisir les résultats</h2>
          <p class="mt-1 text-sm text-slate-600">Renseignez la valeur pour chaque analyse.</p>
        </div>

        <ul class="min-h-0 flex-1 space-y-3 overflow-y-auto pr-1">
          <li
            v-for="(entry, idx) in entries"
            :key="entry.ligne_id"
            class="rounded-2xl border border-slate-200 bg-slate-50 p-4"
          >
            <div class="mb-2 flex flex-wrap items-baseline justify-between gap-2">
              <span class="font-semibold text-slate-900">{{ entry.code_analyse }}</span>
              <span class="text-sm text-slate-500">{{ entry.libelle }}</span>
            </div>
            <label class="grid gap-2 text-sm text-slate-700">
              <span>Valeur<span v-if="entry.unite"> ({{ entry.unite }})</span></span>
              <input
                v-model="entries[idx].valeur"
                type="text"
                required
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
                :placeholder="entry.unite ? `Ex. valeur en ${entry.unite}` : 'Saisir la valeur'"
              />
            </label>
          </li>
        </ul>

        <div class="flex justify-end gap-2 border-t border-slate-100 pt-2">
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
            {{ loading ? 'Enregistrement…' : 'Enregistrer les résultats' }}
          </button>
        </div>
      </form>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, useId, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  lignes: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['confirm', 'cancel'])

const titleId = useId()
const entries = ref([])

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) return
    entries.value = props.lignes.map((l) => ({
      ligne_id: l.id,
      code_analyse: l.code_analyse,
      libelle: l.libelle,
      unite: l.unite_reference || l.resultat?.unite || '',
      valeur: l.resultat?.valeur || '',
    }))
  },
)

function submit() {
  const resultats = entries.value.map((e) => ({
    ligne_id: e.ligne_id,
    valeur: e.valeur.trim(),
    unite: e.unite,
  }))
  emit('confirm', resultats)
}
</script>
