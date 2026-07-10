import { execSync } from 'child_process'
import { existsSync, unlinkSync } from 'fs'
import path from 'path'
import { djangoEnv, projectRoot, resolvePython } from './helpers/env.js'

export default async function globalSetup() {
  const python = resolvePython()
  const dbPath = path.join(projectRoot, djangoEnv.SQLITE_NAME)
  if (existsSync(dbPath)) {
    unlinkSync(dbPath)
  }

  const env = { ...process.env, ...djangoEnv }

  execSync(`${python} manage.py migrate --noinput`, {
    cwd: projectRoot,
    env,
    stdio: 'inherit',
  })
  execSync(`${python} manage.py seed_admin`, {
    cwd: projectRoot,
    env,
    stdio: 'inherit',
  })
  execSync(`${python} manage.py seed_demo`, {
    cwd: projectRoot,
    env,
    stdio: 'inherit',
  })
}
