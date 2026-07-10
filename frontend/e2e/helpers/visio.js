import { e2eApiBase } from './env.js'

/**
 * Prépare une téléconsultation de test (token, créneau ouvert ou futur).
 * @param {import('@playwright/test').APIRequestContext} request
 * @param {{ future?: boolean, token?: string }} [options]
 */
export async function prepareVisioSession(request, { future = false, token = 'e2e-visio-token' } = {}) {
  const params = new URLSearchParams({ token })
  if (future) params.set('future', '1')

  const response = await request.get(`${e2eApiBase}/test/e2e/visio-session/?${params}`)
  if (!response.ok()) {
    throw new Error(`Préparation visio E2E échouée (${response.status()}): ${await response.text()}`)
  }
  return response.json()
}
