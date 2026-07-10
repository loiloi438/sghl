/**
 * Helpers d'authentification UI pour Playwright.
 * Le personnel passe par MFA e-mail (locmem + endpoint DEBUG /test/e2e/mfa-code/).
 */

import { e2eApiBase } from './env.js'

async function waitForMfaCode(request, username, { attempts = 20, delayMs = 400 } = {}) {
  let lastError = ''
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    const response = await request.get(
      `${e2eApiBase}/test/e2e/mfa-code/?username=${encodeURIComponent(username)}`,
    )
    if (response.ok()) {
      const payload = await response.json()
      return payload.code
    }
    lastError = `${response.status()} ${await response.text()}`
    await new Promise((resolve) => setTimeout(resolve, delayMs))
  }
  throw new Error(`Code MFA indisponible pour ${username}: ${lastError}`)
}

export async function loginStaff(page, request, { username, password }) {
  await page.goto('/login', { waitUntil: 'domcontentloaded' })
  await page.locator('#username').fill(username)
  await page.locator('#password').fill(password)

  const loginResponsePromise = page.waitForResponse(
    (resp) => resp.url().includes('/auth/login/') && resp.request().method() === 'POST',
  )
  await page.getByRole('button', { name: /se connecter/i }).click()
  const loginResponse = await loginResponsePromise

  if (loginResponse.status() === 202) {
    const mfaInput = page.locator('#mfa-code')
    await mfaInput.waitFor({ state: 'visible', timeout: 15000 })
    const code = await waitForMfaCode(request, username)
    await mfaInput.fill(code)

    const mfaResponsePromise = page.waitForResponse(
      (resp) => resp.url().includes('/auth/login/mfa/') && resp.request().method() === 'POST',
    )
    const meResponsePromise = page.waitForResponse(
      (resp) => resp.url().includes('/auth/me/') && resp.request().method() === 'GET',
    )
    await page.getByRole('button', { name: /vérifier le code/i }).click()
    const [mfaResponse, meResponse] = await Promise.all([mfaResponsePromise, meResponsePromise])
    if (!mfaResponse.ok()) {
      throw new Error(`Échec MFA (${mfaResponse.status()}): ${await mfaResponse.text()}`)
    }
    if (!meResponse.ok()) {
      throw new Error(`Session non établie après MFA (${meResponse.status()}): ${await meResponse.text()}`)
    }
  } else if (!loginResponse.ok()) {
    throw new Error(`Échec connexion (${loginResponse.status()}): ${await loginResponse.text()}`)
  }

  await page.waitForURL((url) => !url.pathname.includes('/login'), {
    timeout: 45000,
    waitUntil: 'domcontentloaded',
  })
  await page.locator('main, [role="main"]').first().waitFor({ state: 'visible', timeout: 15000 })
}

export async function loginPatient(page, { username, password }) {
  await page.goto('/login')
  await page.locator('#username').fill(username)
  await page.locator('#password').fill(password)
  await page.getByRole('button', { name: /se connecter/i }).click()
  await page.waitForURL(/\/patient/, { timeout: 30000 })
}
