<template>
  <Teleport to="body">
    <div v-if="open && rdv" class="rdv-panel-root" role="dialog" aria-modal="true" aria-labelledby="rdv-panel-title">
      <div class="rdv-panel-backdrop" @click="close" />
      <aside class="rdv-panel">
        <header class="rdv-panel-header">
          <div>
            <p class="rdv-panel-eyebrow">Gestion du rendez-vous</p>
            <h2 id="rdv-panel-title">{{ rdv.patient_nom }}</h2>
            <p class="rdv-panel-meta">
              {{ rdv.numero_dossier }} · Dr {{ rdv.medecin_nom }}
            </p>
          </div>
          <button type="button" class="rdv-panel-close" aria-label="Fermer" @click="close">×</button>
        </header>

        <div class="rdv-panel-summary">
          <div class="summary-item">
            <span class="summary-label">Date actuelle</span>
            <strong>{{ formatDateTime(rdv.date_heure) }}</strong>
          </div>
          <div class="summary-item">
            <span class="summary-label">Motif</span>
            <strong>{{ rdv.motif }}</strong>
          </div>
          <div class="summary-item">
            <span class="summary-label">Statut</span>
            <span class="badge">{{ statutLabel(rdv.statut) }}</span>
          </div>
        </div>

        <p class="rdv-panel-hint">
          Le patient reçoit un e-mail à chaque modification, report ou annulation (si adresse renseignée).
        </p>

        <div v-if="panelError" class="alert alert-error">{{ panelError }}</div>

        <section v-if="canAct" class="rdv-panel-block">
          <h3>Actions rapides</h3>
          <div class="quick-actions">
            <button
              v-if="rdv.statut === 'planifie'"
              type="button"
              class="btn btn-primary"
              :disabled="busy"
              @click="runAction('confirmer')"
            >
              Confirmer
            </button>
            <button
              v-if="rdv.statut === 'confirme'"
              type="button"
              class="btn btn-primary"
              :disabled="busy"
              @click="runAction('terminer')"
            >
              Terminer
            </button>
            <button
              v-if="['planifie', 'confirme'].includes(rdv.statut)"
              type="button"
              class="btn btn-secondary"
              :disabled="busy"
              @click="runAction('absent')"
            >
              Marquer absent
            </button>
          </div>
        </section>

        <section v-if="canAct" class="rdv-panel-block">
          <h3>Modifier ou reporter</h3>
          <form class="panel-form" @submit.prevent="submitModifier">
            <div class="field">
              <label for="rdv-date">Nouvelle date et heure</label>
              <input id="rdv-date" v-model="form.date_heure" type="datetime-local" />
              <span class="field-hint">Laisser inchangé si vous ne modifiez que le motif ou le médecin.</span>
            </div>
            <div class="field">
              <label for="rdv-medecin">Médecin</label>
              <select id="rdv-medecin" v-model="form.medecin_id">
                <option v-for="m in medecins" :key="m.id" :value="String(m.id)">{{ m.nom }}</option>
              </select>
            </div>
            <div class="field">
              <label for="rdv-motif">Motif de consultation</label>
              <input id="rdv-motif" v-model="form.motif" type="text" required />
            </div>
            <div class="field">
              <label for="rdv-duree">Durée (minutes)</label>
              <input id="rdv-duree" v-model.number="form.duree_minutes" type="number" min="15" max="180" step="5" />
            </div>
            <div class="field">
              <label for="rdv-notes">Notes internes</label>
              <textarea id="rdv-notes" v-model="form.notes" rows="2" placeholder="Optionnel" />
            </div>
            <div class="field">
              <label for="rdv-motif-modif">Motif du report / modification (e-mail patient)</label>
              <input
                id="rdv-motif-modif"
                v-model="form.motif_modification"
                type="text"
                placeholder="Ex. Médecin indisponible, report demandé…"
              />
            </div>
            <button type="submit" class="btn btn-primary" :disabled="busy || !hasModifierChanges">
              Enregistrer et notifier le patient
            </button>
          </form>
        </section>

        <section v-if="canAct" class="rdv-panel-block rdv-panel-block--danger">
          <h3>Annuler le rendez-vous</h3>
          <form class="panel-form" @submit.prevent="submitAnnuler">
            <div class="field">
              <label for="rdv-motif-annul">Motif d'annulation (envoyé par e-mail)</label>
              <input
                id="rdv-motif-annul"
                v-model="form.motif_annulation"
                type="text"
                required
                placeholder="Ex. Patient indisponible"
              />
            </div>
            <button type="submit" class="btn btn-danger" :disabled="busy">
              Annuler le rendez-vous
            </button>
          </form>
        </section>

        <p v-else class="empty">Ce rendez-vous ne peut plus être modifié.</p>
      </aside>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import api, { getErrorMessage } from '../api/client.js'

const props = defineProps({
  open: { type: Boolean, default: false },
  rdv: { type: Object, default: null },
  medecins: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:open', 'success'])

const busy = ref(false)
const panelError = ref('')

const statutLabels = {
  planifie: 'Planifié',
  confirme: 'Confirmé',
  annule: 'Annulé',
  termine: 'Terminé',
  absent: 'Absent',
}

const form = reactive({
  date_heure: '',
  medecin_id: '',
  motif: '',
  duree_minutes: 30,
  notes: '',
  motif_modification: '',
  motif_annulation: '',
})

const canAct = computed(() => {
  return props.rdv && ['planifie', 'confirme'].includes(props.rdv.statut)
})

const initialSnapshot = ref('')

function statutLabel(s) {
  return statutLabels[s] || s
}

function formatDateTime(iso) {
  try {
    return new Date(iso).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

function toLocalDatetimeInput(iso) {
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function snapshotForm() {
  return JSON.stringify({
    date_heure: form.date_heure,
    medecin_id: form.medecin_id,
    motif: form.motif,
    duree_minutes: form.duree_minutes,
    notes: form.notes,
    motif_modification: form.motif_modification,
  })
}

const hasModifierChanges = computed(() => {
  if (!props.rdv) return false
  const dateChanged = form.date_heure !== toLocalDatetimeInput(props.rdv.date_heure)
  const fieldsChanged = snapshotForm() !== initialSnapshot.value
  return dateChanged || fieldsChanged
})

function resetForm() {
  if (!props.rdv) return
  form.date_heure = toLocalDatetimeInput(props.rdv.date_heure)
  form.medecin_id = String(props.rdv.medecin_id)
  form.motif = props.rdv.motif
  form.duree_minutes = props.rdv.duree_minutes ?? 30
  form.notes = props.rdv.notes || ''
  form.motif_modification = ''
  form.motif_annulation = ''
  initialSnapshot.value = snapshotForm()
  panelError.value = ''
}

watch(
  () => [props.open, props.rdv?.id],
  () => {
    if (props.open && props.rdv) resetForm()
  },
)

function close() {
  emit('update:open', false)
}

function toIsoDateTime(localValue) {
  if (!localValue) return null
  return new Date(localValue).toISOString()
}

async function runAction(type) {
  if (!props.rdv) return
  const endpoints = {
    confirmer: 'confirmer',
    annuler: 'annuler',
    terminer: 'terminer',
    absent: 'absent',
  }
  busy.value = true
  panelError.value = ''
  try {
    const body = { version: props.rdv.version }
    if (type === 'annuler') {
      body.motif_annulation = form.motif_annulation || 'Annulation'
    }
    await api.post(`/rendez-vous/${props.rdv.id}/${endpoints[type]}/`, body)
    const labels = {
      confirmer: 'Rendez-vous confirmé — e-mail envoyé au patient.',
      terminer: 'Rendez-vous terminé.',
      absent: 'Patient marqué absent.',
      annuler: 'Rendez-vous annulé — e-mail envoyé au patient.',
    }
    emit('success', labels[type] || 'Mis à jour.')
    close()
  } catch (e) {
    panelError.value = getErrorMessage(e)
  } finally {
    busy.value = false
  }
}

async function submitModifier() {
  if (!props.rdv || !hasModifierChanges.value) return
  busy.value = true
  panelError.value = ''
  try {
    const body = {
      version: props.rdv.version,
      motif_modification: form.motif_modification.trim(),
    }
    const newIso = toIsoDateTime(form.date_heure)
    const oldLocal = toLocalDatetimeInput(props.rdv.date_heure)
    if (form.date_heure && form.date_heure !== oldLocal) {
      body.date_heure = newIso
    }
    if (Number(form.medecin_id) !== props.rdv.medecin_id) {
      body.medecin_id = Number(form.medecin_id)
    }
    if (form.motif.trim() !== props.rdv.motif) {
      body.motif = form.motif.trim()
    }
    if (form.duree_minutes !== props.rdv.duree_minutes) {
      body.duree_minutes = form.duree_minutes
    }
    if ((form.notes || '') !== (props.rdv.notes || '')) {
      body.notes = form.notes
    }
    await api.post(`/rendez-vous/${props.rdv.id}/modifier/`, body)
    const msg = body.date_heure
      ? 'Rendez-vous reporté — le patient a été notifié par e-mail.'
      : 'Rendez-vous modifié — le patient a été notifié par e-mail.'
    emit('success', msg)
    close()
  } catch (e) {
    panelError.value = getErrorMessage(e)
  } finally {
    busy.value = false
  }
}

async function submitAnnuler() {
  if (!props.rdv) return
  busy.value = true
  panelError.value = ''
  try {
    await api.post(`/rendez-vous/${props.rdv.id}/annuler/`, {
      version: props.rdv.version,
      motif_annulation: form.motif_annulation.trim() || 'Annulation',
    })
    emit('success', 'Rendez-vous annulé — e-mail envoyé au patient.')
    close()
  } catch (e) {
    panelError.value = getErrorMessage(e)
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.rdv-panel-root {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  justify-content: flex-end;
}

.rdv-panel-backdrop {
  flex: 1;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(4px);
}

.rdv-panel {
  width: min(440px, 100vw);
  max-height: 100vh;
  overflow-y: auto;
  background: var(--color-surface);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  padding: 1.25rem 1.5rem 2rem;
  animation: slideIn 0.22s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0.6;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.rdv-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.rdv-panel-eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-muted);
}

.rdv-panel-header h2 {
  margin: 0;
  font-size: 1.35rem;
}

.rdv-panel-meta {
  margin: 0.35rem 0 0;
  color: var(--color-muted);
  font-size: 0.9rem;
}

.rdv-panel-close {
  border: none;
  background: var(--color-border-soft);
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--radius-sm);
  font-size: 1.4rem;
  line-height: 1;
  cursor: pointer;
  color: var(--color-text);
}

.rdv-panel-close:hover {
  background: var(--color-border);
}

.rdv-panel-summary {
  display: grid;
  gap: 0.65rem;
  padding: 1rem;
  background: var(--color-primary-light);
  border: 1px solid #bfdbfe;
  border-radius: var(--radius);
  margin-bottom: 0.75rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.summary-label {
  font-size: 0.75rem;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.rdv-panel-hint {
  margin: 0 0 1rem;
  font-size: 0.85rem;
  color: var(--color-muted);
  line-height: 1.45;
}

.rdv-panel-block {
  margin-bottom: 1.25rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.rdv-panel-block h3 {
  margin: 0 0 0.75rem;
  font-size: 0.95rem;
}

.rdv-panel-block--danger {
  border-bottom: none;
  padding: 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius);
}

.rdv-panel-block--danger h3 {
  color: var(--color-danger);
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.panel-form .field {
  margin-bottom: 0.85rem;
}

.field-hint {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-muted);
}

.panel-form textarea {
  width: 100%;
  resize: vertical;
  min-height: 3rem;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}

.panel-form .btn {
  width: 100%;
  margin-top: 0.25rem;
}
</style>
