import { computed, ref, watch } from 'vue'
import { messages } from '../i18n/messages.js'

const STORAGE_KEY = 'sghl_locale'
const locale = ref(
  typeof localStorage !== 'undefined' && localStorage.getItem(STORAGE_KEY) === 'en'
    ? 'en'
    : 'fr',
)

watch(locale, (value) => {
  try {
    localStorage.setItem(STORAGE_KEY, value)
    document.documentElement.lang = value
  } catch {
    /* ignore */
  }
})

export function useI18n() {
  const t = (key) => {
    const pack = messages[locale.value] || messages.fr
    return pack[key] || messages.fr[key] || key
  }

  function setLocale(next) {
    locale.value = next === 'en' ? 'en' : 'fr'
  }

  function toggleLocale() {
    setLocale(locale.value === 'fr' ? 'en' : 'fr')
  }

  return {
    locale: computed(() => locale.value),
    t,
    setLocale,
    toggleLocale,
  }
}
