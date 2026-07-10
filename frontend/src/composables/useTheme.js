import { ref, watch } from 'vue'

const STORAGE_KEY = 'sghl-theme'
const theme = ref('light')

function applyTheme(value) {
  const root = document.documentElement
  root.dataset.theme = value
  root.style.colorScheme = value
}

function initTheme() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'light') {
    theme.value = 'light'
  } else if (saved === 'dark') {
    // Ancien mode sombre : bascule vers le thème clair harmonisé
    theme.value = 'light'
    localStorage.setItem(STORAGE_KEY, 'light')
  } else {
    theme.value = 'light'
  }
  applyTheme(theme.value)
}

function toggleTheme() {
  // Interface harmonisée en mode clair uniquement (lisibilité)
  theme.value = 'light'
}

watch(theme, (value) => {
  localStorage.setItem(STORAGE_KEY, value)
  applyTheme(value)
})

export function useTheme() {
  return { theme, toggleTheme, initTheme, isDark: () => theme.value === 'dark' }
}

export { initTheme }
