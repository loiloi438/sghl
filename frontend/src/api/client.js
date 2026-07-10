import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

export function unwrapList(data) {
  if (Array.isArray(data)) return data
  if (data?.items) return data.items
  return []
}

export function getErrorMessage(error) {
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail
    return typeof detail === 'string' ? detail : JSON.stringify(detail)
  }
  return error.message || 'Erreur réseau'
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
    if (error.response?.status === 401 && !original._retry) {
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
        }
      }
    }
    return Promise.reject(error)
  },
)

export default api
