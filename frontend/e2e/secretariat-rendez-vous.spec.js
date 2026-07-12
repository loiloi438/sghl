import { test, expect } from '@playwright/test'
import { loginStaff } from './helpers/auth.js'
import {
  e2eApiBase,
  patientCredentials,
  secretaryCredentials,
} from './helpers/env.js'

test.describe('Workflow rendez-vous secrétariat', () => {
  test('une demande patient en attente apparaît et peut être validée', async ({
    page,
    request,
  }) => {
    const loginResponse = await request.post(`${e2eApiBase}/auth/login/`, {
      data: patientCredentials,
    })
    expect(loginResponse.ok()).toBeTruthy()
    const tokens = await loginResponse.json()
    const headers = { Authorization: `Bearer ${tokens.access_token}` }

    const medecinsResponse = await request.get(
      `${e2eApiBase}/patient/rendez-vous/medecins/`,
      { headers },
    )
    expect(medecinsResponse.ok()).toBeTruthy()
    const medecinsPayload = await medecinsResponse.json()
    const medecins = medecinsPayload.items ?? medecinsPayload
    expect(medecins.length).toBeGreaterThan(0)

    const motif = `Contrôle E2E ${Date.now()}`
    const dateHeure = new Date()
    dateHeure.setUTCDate(dateHeure.getUTCDate() + 45)
    dateHeure.setUTCHours(10, Math.floor(Math.random() * 45), 0, 0)

    const createResponse = await request.post(
      `${e2eApiBase}/patient/rendez-vous/`,
      {
        headers,
        data: {
          medecin_id: medecins[0].id,
          date_heure: dateHeure.toISOString(),
          motif,
          duree_minutes: 30,
          type_consultation: 'presentiel',
          email: 'patient@sghl.local',
          email_confirm: 'patient@sghl.local',
          telephone: '+242060000000',
          adresse: 'Brazzaville',
        },
      },
    )
    expect(createResponse.ok()).toBeTruthy()
    const created = await createResponse.json()
    expect(created.statut).toBe('en_attente')

    await loginStaff(page, request, secretaryCredentials)
    await expect(page).toHaveURL(/\/secretariat/)
    await expect(page.getByRole('heading', { name: /rendez-vous en attente/i })).toBeVisible()

    const row = page.getByRole('row').filter({ hasText: motif })
    await expect(row).toBeVisible()
    await row.getByRole('button', { name: /valider/i }).click()
    await expect(page.getByText(/rendez-vous validé/i)).toBeVisible()
    await expect(row).not.toBeVisible()
  })
})
