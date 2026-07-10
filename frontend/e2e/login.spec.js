import { test, expect } from '@playwright/test'

test('connexion médecin affiche le tableau de bord', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel(/identifiant/i).fill('medecin')
  await page.getByLabel(/mot de passe/i).fill('Medecin@SGHL2026')
  await page.getByRole('button', { name: /se connecter/i }).click()
  await expect(page).toHaveURL(/\/(dashboard)?$/, { timeout: 15000 })
  await expect(page.getByRole('heading', { name: /tableau de bord/i })).toBeVisible()
})
