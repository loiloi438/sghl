import { ref, watch } from 'vue'

const STORAGE_KEY = 'sghl-theme'
const theme = ref('human-care')

function applyTheme(value) {
  const root = document.documentElement
  root.dataset.theme = value
  root.style.colorScheme = value === 'tech-health' ? 'dark' : 'light'
}

function initTheme() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'human-care' || saved === 'tech-health') {
    theme.value = saved
  } else {
    theme.value = 'human-care'
  }
  applyTheme(theme.value)
}

function setPortalTheme(portal) {
  const next = portal === 'staff' ? 'tech-health' : 'human-care'
  theme.value = next
  localStorage.setItem(STORAGE_KEY, next)
  applyTheme(next)
}

function toggleTheme() {
  theme.value = theme.value === 'tech-health' ? 'human-care' : 'tech-health'
}

watch(theme, (value) => {
  localStorage.setItem(STORAGE_KEY, value)
  applyTheme(value)
})

export function useTheme() {
  return {
    theme,
    toggleTheme,
    initTheme,
    setPortalTheme,
    isDark: () => theme.value === 'tech-health',
    isHumanCare: () => theme.value === 'human-care',
    isTechHealth: () => theme.value === 'tech-health',
  }
}

export { initTheme, setPortalTheme }
