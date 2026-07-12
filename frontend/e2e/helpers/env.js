import { existsSync } from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export const projectRoot = path.resolve(__dirname, '../../..')
export const frontendRoot = path.resolve(__dirname, '../..')

export function resolvePython() {
  if (process.env.SGHL_PYTHON) return process.env.SGHL_PYTHON

  const winVenv = path.join(projectRoot, '.venv', 'Scripts', 'python.exe')
  const unixVenv = path.join(projectRoot, '.venv', 'bin', 'python')
  if (existsSync(winVenv)) return winVenv
  if (existsSync(unixVenv)) return unixVenv

  return process.platform === 'win32' ? 'python' : 'python3'
}

/** Variables d'environnement Django pour les tests E2E locaux / CI. */
export const djangoEnv = {
  DJANGO_SETTINGS_MODULE: 'sghl.settings',
  DEBUG: 'True',
  SECRET_KEY: process.env.SECRET_KEY || 'e2e-test-secret-key',
  JWT_SECRET: process.env.JWT_SECRET || 'e2e-test-jwt-secret',
  DB_ENGINE: process.env.DB_ENGINE || 'sqlite',
  SQLITE_NAME: process.env.SQLITE_NAME || 'e2e-test.sqlite3',
  EMAIL_BACKEND: 'django.core.mail.backends.locmem.EmailBackend',
  EMAIL_NOTIFICATIONS_ENABLED: 'True',
  OTP_MODE: 'development',
  LOGIN_RATE_LIMIT_ENABLED: 'False',
  SGHL_FRONTEND_URL: process.env.SGHL_FRONTEND_URL || `http://127.0.0.1:${process.env.E2E_WEB_PORT || '5174'}`,
  SGHL_ADMIN_PASSWORD: process.env.SGHL_ADMIN_PASSWORD || 'Admin@SGHL2026',
  SGHL_SEED_ADMIN: 'true',
  SGHL_SEED_DEMO: 'true',
}

export const staffCredentials = {
  username: 'medecin',
  password: 'Medecin@SGHL2026',
}

export const patientCredentials = {
  username: 'patient',
  password: 'Patient@SGHL2026',
}

export const secretaryCredentials = {
  username: 'samantha',
  password: 'Secretaire@SGHL2026',
}

const apiPort = process.env.E2E_API_PORT || '8010'
const webPort = process.env.E2E_WEB_PORT || '5174'
export const e2eApiBase = process.env.E2E_API_BASE || `http://127.0.0.1:${apiPort}/api/v1`
export const e2eWebBase = process.env.E2E_WEB_BASE || `http://127.0.0.1:${webPort}`
