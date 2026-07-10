<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">
      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Pharmacie</h1>
            <p class="mt-1 text-sm text-slate-600">Stock, dispensation et ordonnances validées</p>
          </div>
          <button class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" type="button" @click="loadAll">Actualiser</button>
        </div>
      </div>

      <div v-if="message" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
      <div v-if="error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</div>

      <div class="grid gap-4 xl:grid-cols-3">
        <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Stock — alertes</h2>
          <div class="mt-4 space-y-2 text-sm text-slate-700">
            <div v-if="alertes.length === 0" class="text-slate-500">Aucune alerte stock bas.</div>
            <ul v-else class="space-y-2 list-inside">
              <li v-for="m in alertes" :key="m.id" class="rounded-2xl bg-slate-50 px-4 py-3">
                <span class="font-semibold text-slate-900">{{ m.libelle }}</span> : {{ m.quantite_stock }} {{ m.unite }} (seuil {{ m.seuil_alerte }})
              </li>
            </ul>
          </div>
        </section>

        <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Péremption</h2>
          <div class="mt-4 space-y-2 text-sm text-slate-700">
            <div v-if="peremptionAlertes.length === 0" class="text-slate-500">Aucun lot périmé ou proche de la date.</div>
            <ul v-else class="space-y-3">
              <li v-for="m in peremptionAlertes" :key="'p-' + m.id" class="rounded-2xl border border-slate-200 p-4" :class="m.est_perime ? 'bg-rose-50 text-rose-700' : m.peremption_proche ? 'bg-amber-50 text-amber-700' : 'bg-slate-50 text-slate-700'">
                <div class="flex flex-wrap items-center gap-2 text-sm">
                  <span class="font-semibold">{{ m.libelle }}</span>
                  <span>— {{ formatPeremption(m) }}</span>
                </div>
                <div class="mt-2 text-xs uppercase tracking-[0.2em]">
                  <span v-if="m.est_perime" class="rounded-full bg-rose-100 px-2 py-1 font-semibold">Périmé</span>
                  <span v-else-if="m.peremption_proche" class="rounded-full bg-amber-100 px-2 py-1 font-semibold">Proche</span>
                </div>
              </li>
            </ul>
          </div>
        </section>

        <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Approvisionnement rapide</h2>
          <form class="mt-5 space-y-4">
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">Médicament</label>
              <select v-model="appro.medId" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500">
                <option value="">— Sélectionner —</option>
                <option v-for="m in stock" :key="m.id" :value="m.id">{{ m.code }} — {{ m.libelle }} ({{ m.quantite_stock }})</option>
              </select>
            </div>
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">Quantité à ajouter</label>
              <input v-model.number="appro.quantite" type="number" min="1" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <button class="rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700" :disabled="!appro.medId" @click.prevent="approvisionner">Approvisionner</button>
          </form>
        </section>
      </div>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Prescriptions à dispenser</h2>
        <div v-if="!auth.canPharmacie" class="mt-4 text-sm text-slate-500">Réservé au pharmacien.</div>
        <div v-else-if="aDispenser.length === 0" class="mt-4 text-sm text-slate-500">Aucune prescription en attente.</div>
        <div v-else class="mt-4 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Patient</th>
                <th class="px-3 py-3 font-medium">Médicaments</th>
                <th class="px-3 py-3 font-medium">Validée le</th>
                <th class="px-3 py-3 font-medium">Statut pharma</th>
                <th class="px-3 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="p in aDispenser" :key="p.prescription_id" class="hover:bg-slate-50">
                <td class="px-3 py-3 text-slate-700">{{ p.patient_nom }} ({{ p.numero_dossier }})</td>
                <td class="px-3 py-3 text-slate-700">{{ p.medicaments.join(', ') }}</td>
                <td class="px-3 py-3 text-slate-700">{{ formatDate(p.validee_le) }}</td>
                <td class="px-3 py-3 text-slate-700">{{ p.deja_en_pharmacie ? 'Ordre créé' : 'À traiter' }}</td>
                <td class="px-3 py-3">
                  <button v-if="!p.deja_en_pharmacie" class="rounded-2xl bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-700" @click.prevent="creerOrdre(p.prescription_id)">Créer ordre</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Ordres de dispensation</h2>
        <div v-if="ordres.length === 0" class="mt-4 text-sm text-slate-500">Aucun ordre.</div>
        <div v-else class="mt-4 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Patient</th>
                <th class="px-3 py-3 font-medium">Statut</th>
                <th class="px-3 py-3 font-medium">Lignes</th>
                <th class="px-3 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="o in ordres" :key="o.id" class="hover:bg-slate-50">
                <td class="px-3 py-3 text-slate-700">{{ o.patient_nom }}</td>
                <td class="px-3 py-3"><span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600">{{ statutLabel(o.statut) }}</span></td>
                <td class="px-3 py-3">
                  <div class="flex flex-wrap gap-2">
                    <span v-for="l in o.lignes" :key="l.id" class="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700">{{ l.medicament }} x{{ l.quantite }}</span>
                  </div>
                </td>
                <td class="px-3 py-3 flex flex-wrap gap-2">
                  <button v-if="o.statut === 'en_attente' && auth.canPharmacie" class="rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" @click.prevent="preparer(o)">Préparer</button>
                  <button v-if="['en_attente', 'prepare'].includes(o.statut) && auth.canPharmacie" class="rounded-2xl bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-700" @click.prevent="requestDispenser(o)">Dispenser</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-900">Inventaire</h2>
        <div class="mt-4 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr class="text-left text-slate-600">
                <th class="px-3 py-3 font-medium">Code</th>
                <th class="px-3 py-3 font-medium">Libellé</th>
                <th class="px-3 py-3 font-medium">Stock</th>
                <th class="px-3 py-3 font-medium">Seuil</th>
                <th class="px-3 py-3 font-medium">Péremption</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="m in stock" :key="m.id" class="hover:bg-slate-50" :class="m.est_perime ? 'bg-rose-50' : m.peremption_proche ? 'bg-amber-50' : m.stock_bas ? 'bg-amber-50/50' : ''">
                <td class="px-3 py-3 text-slate-700">{{ m.code }}</td>
                <td class="px-3 py-3 text-slate-700">{{ m.libelle }}</td>
                <td class="px-3 py-3 text-slate-700">{{ m.quantite_stock }} {{ m.unite }}</td>
                <td class="px-3 py-3 text-slate-700">{{ m.seuil_alerte }}</td>
                <td class="px-3 py-3 text-slate-700">{{ formatPeremption(m) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>

  <ConfirmDialog
    :open="confirmDispense.open"
    title="Dispenser l'ordonnance"
    :message="confirmDispense.message"
    confirm-label="Confirmer la dispensation"
    :loading="saving"
    @confirm="confirmDispensation"
    @cancel="confirmDispense.open = false"
  />
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import api, { getErrorMessage, unwrapList } from '../api/client.js'
import { showToast } from '../composables/useToast.js'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const stock = ref([])
const alertes = ref([])
const peremptionAlertes = ref([])
const aDispenser = ref([])
const ordres = ref([])
const error = ref('')
const message = ref('')
const saving = ref(false)
const confirmDispense = ref({ open: false, message: '', ordre: null })
const appro = reactive({ medId: '', quantite: 50 })

const statutLabels = {
  en_attente: 'En attente',
  prepare: 'Préparé',
  dispense: 'Dispensé',
  annule: 'Annulé',
}

function statutLabel(s) {
  return statutLabels[s] || s
}

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('fr-FR')
  } catch {
    return iso
  }
}

function formatPeremption(m) {
  if (!m.date_peremption) return '—'
  try {
    return new Date(m.date_peremption).toLocaleDateString('fr-FR')
  } catch {
    return m.date_peremption
  }
}

async function loadAll() {
  error.value = ''
  try {
    const [stockRes, alertesRes, peremptionRes, ordresRes] = await Promise.all([
      api.get('/pharmacie/stock/'),
      api.get('/pharmacie/stock/alertes/'),
      api.get('/pharmacie/stock/peremption/'),
      api.get('/pharmacie/ordres-dispensation/'),
    ])
    stock.value = unwrapList(stockRes.data)
    alertes.value = unwrapList(alertesRes.data)
    peremptionAlertes.value = unwrapList(peremptionRes.data)
    ordres.value = unwrapList(ordresRes.data)

    if (auth.canPharmacie) {
      const rxRes = await api.get('/pharmacie/prescriptions-a-dispenser/')
      aDispenser.value = unwrapList(rxRes.data)
    }
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function approvisionner() {
  error.value = ''
  message.value = ''
  try {
    await api.post(`/pharmacie/stock/${appro.medId}/approvisionner/`, {
      quantite: appro.quantite,
    })
    message.value = 'Stock approvisionné.'
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function creerOrdre(prescriptionId) {
  error.value = ''
  message.value = ''
  try {
    await api.post(`/prescriptions/${prescriptionId}/ordre-dispensation/`)
    message.value = 'Ordre de dispensation créé.'
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function preparer(ordre) {
  error.value = ''
  try {
    await api.post(`/pharmacie/ordres-dispensation/${ordre.id}/preparer/`, {
      version: ordre.version,
    })
    message.value = 'Ordre préparé.'
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

function requestDispenser(ordre) {
  confirmDispense.value = {
    open: true,
    message: `Confirmer la dispensation pour ${ordre.patient_nom} ?`,
    ordre,
  }
}

async function confirmDispensation() {
  const ordre = confirmDispense.value.ordre
  if (!ordre) return
  error.value = ''
  saving.value = true
  try {
    await api.post(`/pharmacie/ordres-dispensation/${ordre.id}/dispenser/`, {
      version: ordre.version,
    })
    confirmDispense.value.open = false
    message.value = 'Médicaments dispensés — stock mis à jour.'
    showToast('Dispensation enregistrée.', 'success')
    await loadAll()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

onMounted(loadAll)
</script>

