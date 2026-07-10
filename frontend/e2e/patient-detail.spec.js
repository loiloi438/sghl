import { test, expect } from '@playwright/test'
import { loginStaff } from './helpers/auth.js'
import { staffCredentials } from './helpers/env.js'

test.describe('Fiche patient staff', () => {
  test('ouvre le dossier depuis la liste patients', async ({ page, request }) => {
    await loginStaff(page, request, staffCredentials)
    await page.goto('/patients')
    await expect(page.getByRole('main').getByRole('heading', { name: /^patients$/i })).toBeVisible()

    const dossierLink = page.getByRole('link', { name: /voir dossier/i }).first()
    await expect(dossierLink).toBeVisible()
    await dossierLink.click()

    await expect(page).toHaveURL(/\/patients\/[0-9a-f-]+/)
    await expect(page.getByText(/dossier patient/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /^résumé$/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /hospitalisation/i })).toBeVisible()
  })
})
