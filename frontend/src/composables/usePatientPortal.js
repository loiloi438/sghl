export function formatPatientDate(iso) {
  if (!iso) return '—'
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

export function formatMontant(value) {
  if (value == null || value === '') return '—'
  const n = Number(value)
  return Number.isNaN(n) ? value : n.toLocaleString('fr-FR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

export function prescriptionStatutLabel(statut) {
  const map = {
    validee: 'Validée',
    brouillon: 'Brouillon',
    annulee: 'Annulée',
  }
  return map[statut] || statut
}

export function factureStatutLabel(statut) {
  const map = {
    payee: 'Payée',
    partiellement_payee: 'Partiellement payée',
    validee: 'Validée',
    brouillon: 'Brouillon',
    annulee: 'Annulée',
  }
  return map[statut] || statut
}

export function rdvStatutLabel(statut) {
  const map = {
    planifie: 'Planifié',
    confirme: 'Confirmé',
    termine: 'Terminé',
    annule: 'Annulé',
    absent: 'Absent',
  }
  return map[statut] || statut
}

export function typeConsultationLabel(type) {
  return type === 'teleconsultation' ? 'Téléconsultation' : 'Présentiel'
}

export function constanteSummary(c) {
  const parts = []
  if (c.temperature != null) parts.push(`T° ${c.temperature}°C`)
  if (c.tension_systolique != null) {
    parts.push(`TA ${c.tension_systolique}/${c.tension_diastolique ?? '—'}`)
  }
  if (c.frequence_cardiaque != null) parts.push(`FC ${c.frequence_cardiaque}`)
  if (c.saturation_o2 != null) parts.push(`SpO₂ ${c.saturation_o2}%`)
  return parts.length ? parts.join(' · ') : 'Mesure enregistrée'
}

export const patientNavLinks = [
  { to: '/patient', label: 'Accueil', exact: true },
  { to: '/patient/rendez-vous', label: 'Rendez-vous' },
  { to: '/patient/soins', label: 'Soins' },
  { to: '/patient/prescriptions', label: 'Prescriptions' },
  { to: '/patient/laboratoire', label: 'Laboratoire' },
  { to: '/patient/factures', label: 'Factures' },
  { to: '/patient/notifications', label: 'Notifications', badge: true },
  { to: '/patient/profil', label: 'Profil' },
]
