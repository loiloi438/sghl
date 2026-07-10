import { defineConfig, devices } from '@playwright/test'
import { djangoEnv, frontendRoot, projectRoot, resolvePython } from './e2e/helpers/env.js'

const python = resolvePython()
const backendEnv = { ...process.env, ...djangoEnv }

const apiPort = process.env.E2E_API_PORT || '8010'
const webPort = process.env.E2E_WEB_PORT || '5174'
const apiUrl = `http://127.0.0.1:${apiPort}`
const webUrl = `http://127.0.0.1:${webPort}`

export default defineConfig({
  testDir: './e2e',
  timeout: 90000,
  expect: { timeout: 15000 },
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: process.env.CI ? [['github'], ['list']] : [['list']],
  globalSetup: './e2e/global-setup.js',
  use: {
    baseURL: webUrl,
    headless: true,
    trace: 'on-first-retry',
    ...devices['Desktop Chrome'],
  },
  webServer: [
    {
      command: `${python} manage.py runserver ${apiPort} --noreload`,
      cwd: projectRoot,
      url: `${apiUrl}/api/v1/sante/`,
      reuseExistingServer: false,
      timeout: 180000,
      env: backendEnv,
    },
    {
      command: `npm run dev -- --host 127.0.0.1 --port ${webPort}`,
      cwd: frontendRoot,
      url: webUrl,
      reuseExistingServer: false,
      timeout: 120000,
      env: {
        ...process.env,
        VITE_DEV_API_TARGET: apiUrl,
        VITE_API_BASE_URL: `${apiUrl}/api/v1`,
      },
    },
  ],
})
