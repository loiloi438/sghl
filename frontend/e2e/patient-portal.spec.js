import { test, expect } from '@playwright/test'
import { loginPatient } from './helpers/auth.js'
import { patientCredentials } from './helpers/env.js'

test.describe('Portail patient', () => {
  test('connexion patient affiche Mon espace', async ({ page }) => {
    await loginPatient(page, patientCredentials)
    await expect(page.getByRole('heading', { name: /mon espace/i })).toBeVisible()
    await expect(page.getByText(/dossier/i).first()).toBeVisible()
  })

  test('navigation vers Mes rendez-vous', async ({ page }) => {
    await loginPatient(page, patientCredentials)
    await page.getByRole('link', { name: /^rendez-vous$/i }).click()
    await expect(page).toHaveURL(/\/patient\/rendez-vous/)
    await expect(page.getByRole('heading', { name: /mes rendez-vous/i })).toBeVisible()
    await expect(page.getByRole('heading', { name: /nouveau rendez-vous/i })).toBeVisible()
  })
})
