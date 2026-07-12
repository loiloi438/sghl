import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000,
})

export function unwrapList(data) {
  if (Array.isArray(data)) return data
  if (data?.items) return data.items
  return []
}

function humanizeDetail(detail) {
  if (typeof detail === 'string') {
    const lower = detail.toLowerCase()
    if (lower.includes('unauthorized') || lower.includes('not authenticated')) {
      return 'Votre session a expiré. Reconnectez-vous pour continuer 💙'
    }
    if (lower.includes('forbidden') || lower.includes('accès refusé') || lower.includes('acces refuse')) {
      return 'Cette action est réservée à votre rôle ou au personnel autorisé 💙'
    }
    return detail
  }
  if (Array.isArray(detail)) {
    return detail.map((item) => humanizeDetail(item)).join(' ')
  }
  if (detail && typeof detail === 'object') {
    return detail.msg || detail.message || 'Une erreur est survenue. Réessayez.'
  }
  return 'Une erreur est survenue. Réessayez.'
}

export function getErrorMessage(error) {
  const status = error.response?.status
  const detail = error.response?.data?.detail

  if (status === 401) {
    return 'Votre session a expiré. Reconnectez-vous pour continuer 💙'
  }
  if (status === 403) {
    return detail
      ? humanizeDetail(detail)
      : 'Cette action est réservée à votre rôle ou au personnel autorisé 💙'
  }
  if (status === 429) {
    return 'Trop de tentatives. Patientez quelques minutes avant de réessayer.'
  }
  if (status >= 500) {
    return 'Nos services sont temporairement indisponibles. Réessayez dans un instant.'
  }
  if (detail) {
    return humanizeDetail(detail)
  }
  const message = error.message || ''
  if (/network error|timeout|failed to fetch/i.test(message)) {
    return 'Connexion momentanément indisponible. Vérifiez votre réseau et réessayez 💙'
  }
  return message || 'Erreur réseau'
}

function redirectToLogin() {
  const path = window.location.pathname + window.location.search
  if (path.startsWith('/login')) return
  window.location.assign(`/login?redirect=${encodeURIComponent(path)}`)
}

export async function downloadPdf(path, filename) {
  const response = await api.get(path, { responseType: 'blob' })
  const blob = new Blob([response.data], { type: 'application/pdf' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename || 'document.pdf'
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export async function downloadBlob(path, filename, mimeType = 'application/octet-stream') {
  const response = await api.get(path, { responseType: 'blob' })
  const blob = new Blob([response.data], { type: mimeType })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename || 'document.pdf'
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sghl_access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('sghl_refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post(
            `${import.meta.env.VITE_API_BASE_URL || '/api/v1'}/auth/refresh/`,
            { refresh_token: refresh },
          )
          localStorage.setItem('sghl_access_token', data.access_token)
          localStorage.setItem('sghl_refresh_token', data.refresh_token)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return api(original)
        } catch {
          localStorage.removeItem('sghl_access_token')
          localStorage.removeItem('sghl_refresh_token')
          redirectToLogin()
        }
      } else {
        redirectToLogin()
      }
    }
    return Promise.reject(error)
  },
)

export default api
