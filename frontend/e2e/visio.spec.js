import { test, expect } from '@playwright/test'
import { loginStaff } from './helpers/auth.js'
import { staffCredentials } from './helpers/env.js'
import { prepareVisioSession } from './helpers/visio.js'

test.describe('Téléconsultation visio', () => {
  test('lien public ouvre la salle et affiche Jitsi', async ({ page, request }) => {
    const session = await prepareVisioSession(request)
    expect(session.can_join).toBe(true)

    await page.goto(`/visio/${session.token}`)
    await expect(page.getByRole('heading', { name: /salle de visioconférence/i })).toBeVisible()
    await expect(page.getByText(session.motif)).toBeVisible()
    await expect(page.getByText(session.patient_name)).toBeVisible()
    await expect(page.getByText(new RegExp(session.doctor_name, 'i'))).toBeVisible()
    await expect(page.getByText(/la salle est ouverte/i)).toBeVisible()

    await page.getByLabel(/nom affiché dans la visio/i).fill('Patient E2E')
    await page.getByRole('button', { name: /rejoindre la consultation/i }).click()

    const iframe = page.locator('iframe[title="Salle de téléconsultation SGHL"]')
    await expect(iframe).toBeVisible()
    const src = await iframe.getAttribute('src')
    expect(src).toContain('meet.jit.si')
    expect(src).toContain('sghl-visio')
    expect(src).toContain(encodeURIComponent('Patient E2E'))
  })

  test('token invalide affiche une erreur', async ({ page }) => {
    await page.goto('/visio/token-inexistant-e2e')
    await expect(page.getByRole('heading', { name: /lien indisponible/i })).toBeVisible()
    await expect(page.getByText(/invalide|expiré/i)).toBeVisible()
  })

  test('consultation future affiche le message d’attente', async ({ page, request }) => {
    const session = await prepareVisioSession(request, { future: true, token: 'e2e-visio-future' })
    expect(session.can_join).toBe(false)

    await page.goto(`/visio/${session.token}`)
    await expect(page.getByText(/la salle ouvrira/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /rejoindre la consultation/i })).toHaveCount(0)
  })

  test('médecin rejoint depuis le module téléconsultation', async ({ page, request }) => {
    test.setTimeout(120000)
    await loginStaff(page, request, staffCredentials)
    const session = await prepareVisioSession(request)

    await page.goto('/teleconsultation', { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('main').getByRole('heading', { name: /téléconsultation/i })).toBeVisible()

    const row = page.getByRole('row').filter({ hasText: session.patient_name }).filter({ hasText: session.date_time })
    await expect(row).toBeVisible()
    await row.getByRole('button', { name: /rejoindre/i }).click()

    await expect(page).toHaveURL(new RegExp(`/visio/${session.token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`))
    await expect(page.getByText(session.motif)).toBeVisible()
    await expect(page.getByText(/la salle est ouverte/i)).toBeVisible()
  })
})
