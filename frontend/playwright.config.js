import { defineConfig } from '@playwright/test'
import { fileURLToPath } from 'url'
import path from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const projectRoot = path.resolve(__dirname, '..')
const pythonPath = path.resolve(projectRoot, '.venv', 'Scripts', 'python.exe')

export default defineConfig({
  testDir: './e2e',
  timeout: 60000,
  use: {
    baseURL: 'http://127.0.0.1:5173',
    headless: true,
  },
  webServer: [
    {
      command: `${pythonPath} manage.py runserver 8000`,
      cwd: projectRoot,
      url: 'http://127.0.0.1:8000/api/v1/sante/',
      reuseExistingServer: true,
      timeout: 120000,
    },
    {
      command: 'npm run dev',
      url: 'http://127.0.0.1:5173',
      reuseExistingServer: true,
      timeout: 120000,
    },
  ],
})
