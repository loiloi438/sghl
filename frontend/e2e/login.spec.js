import { test, expect } from '@playwright/test'
import { loginStaff } from './helpers/auth.js'
import { staffCredentials } from './helpers/env.js'

test.describe('Connexion staff', () => {
  test('médecin avec MFA accède au module rendez-vous', async ({ page, request }) => {
    await loginStaff(page, request, staffCredentials)
    await expect(page).toHaveURL(/\/rendez-vous/)
    await expect(page.getByRole('heading', { name: /rendez-vous/i }).first()).toBeVisible()
  })
})
